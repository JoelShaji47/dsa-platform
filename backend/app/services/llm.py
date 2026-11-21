"""Chat LLM provider: Gemini key rotation with Groq fallback.

Additive only — hints/reviews keep using ``app.services.gemini`` directly.
This module serves the interactive Solve-page coach, where bursty per-user
traffic can exhaust a single Gemini key.

Order: Gemini keys round-robin (per-key 60s cooldown on 429/5xx/quota)
→ Groq (OpenAI-compatible) → raise LLMError.

A key the provider *rejects* (401 / UNAUTHENTICATED / "API key not valid") is
different from a key that is merely busy: it will never work, so it is parked
for hours instead of being retried on every request. The message on LLMError is
user-facing (the API copies it into a 503 detail), so it stays short and never
contains provider JSON.
"""

import logging
import threading
import time

import httpx
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 60.0
# A rejected key cannot recover by itself — only a deploy/env change fixes it.
INVALID_KEY_COOLDOWN_SECONDS = 6 * 60 * 60
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

UNAVAILABLE_MESSAGE = (
    "The AI coach is temporarily unavailable — please try again in a moment."
)


class LLMError(Exception):
    """Raised when no chat provider can answer. Safe to show to the user."""


_lock = threading.Lock()
_next_index = 0
_cooldown_until: dict[str, float] = {}
_groq_cooldown_until = 0.0


def _mask(key: str) -> str:
    return f"…{key[-4:]}" if len(key) > 4 else "…?"


def _chat_keys() -> list[str]:
    return settings.gemini_chat_keys


def _call_gemini(key: str, system: str, prompt: str, max_tokens: int = 700) -> str:
    # No SDK retries (we rotate keys ourselves); hard timeout per attempt.
    client = genai.Client(
        api_key=key,
        http_options={
            "timeout": 60_000,
            "retry_options": {"attempts": 1},
        },
    )
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.4,
            max_output_tokens=max_tokens,
            # gemini-3.x-flash thinks before answering and spends the SAME
            # max_output_tokens budget on those thought tokens, so at 700-900
            # the visible reply is cut off at FinishReason.MAX_TOKENS and
            # arrives as truncated JSON → analyzer 503s. These calls are short
            # JSON/debrief replies; turn thinking off so the whole budget
            # goes to the answer. (Only matters for thinking-capable models.)
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    if not response.text:
        raise LLMError("Gemini returned an empty response")
    candidate = response.candidates[0] if response.candidates else None
    if candidate is not None and getattr(candidate.finish_reason, "name", None) == "MAX_TOKENS":
        raise LLMError("Gemini reply was truncated at max_tokens")
    return response.text


def _call_groq(system: str, prompt: str, max_tokens: int = 700) -> str:
    global _groq_cooldown_until

    if not settings.groq_configured:
        raise LLMError("Groq is not configured")
    if _groq_cooldown_until > time.monotonic():
        raise LLMError("Groq is cooling down")
    try:
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json={
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": max_tokens,
            },
            timeout=120.0,
        )
    except Exception as exc:
        raise LLMError(f"Groq request failed: {exc}") from exc
    if resp.status_code in (401, 403):
        # A rejected Groq key is permanent too; stop burning a call per request.
        _groq_cooldown_until = time.monotonic() + INVALID_KEY_COOLDOWN_SECONDS
        raise LLMError("Groq rejected the API key")
    if resp.status_code == 429:
        _groq_cooldown_until = time.monotonic() + COOLDOWN_SECONDS
        raise LLMError("Groq rate-limited (429)")
    if resp.status_code >= 400:
        raise LLMError(f"Groq request failed: HTTP {resp.status_code}")
    try:
        text = resp.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        raise LLMError(f"Groq bad response: {exc}") from exc
    if not text or not text.strip():
        raise LLMError("Groq returned an empty response")
    return text.strip()


def _is_invalid_key(exc: Exception) -> bool:
    """True when the provider rejected the credential itself.

    Gemini reports a bad key as 401 UNAUTHENTICATED with either
    ``API key not valid`` or ``ACCESS_TOKEN_TYPE_UNSUPPORTED`` (the API key was
    mistaken for an OAuth access token). Groq reports it as 401 too.
    """
    msg = str(exc).lower()
    return any(
        s in msg
        for s in (
            "unauthenticated",
            "api key not valid",
            "api_key_invalid",
            "invalid api key",
            "access_token_type_unsupported",
            "permission_denied",
            "401",
            "403",
        )
    )


def _is_retryable(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        s in msg
        for s in (
            "429", "500", "502", "503", "quota", "exceeded",
            "rate", "overloaded", "unavailable", "timeout", "empty response",
        )
    )


def generate_chat(system: str, prompt: str, prefer: str | None = None, max_tokens: int = 700) -> tuple[str, str]:
    """Return (reply_text, provider_label). Raises LLMError when all fail.

    Default order: Gemini keys round-robin (per-key 60s cooldown on
    429/5xx/quota, 6h on a rejected key) → Groq → error. prefer="groq"
    flips the order for bulk/background workloads where Groq throughput
    matters more.
    """
    errors: list[str] = []
    if prefer == "groq":
        try:
            return _call_groq(system, prompt, max_tokens), "groq"
        except Exception as exc:
            errors.append(f"groq={exc}")

    keys = _chat_keys()
    now = time.monotonic()
    with _lock:
        global _next_index
        start = _next_index % len(keys) if keys else 0

    invalid_keys = 0
    cooling_keys = 0
    if keys:
        for i in range(len(keys)):
            key = keys[(start + i) % len(keys)]
            if _cooldown_until.get(key, 0) > now:
                cooling_keys += 1
                errors.append(f"gemini:{_mask(key)}=cooldown")
                continue
            try:
                text = _call_gemini(key, system, prompt, max_tokens)
            except Exception as exc:
                errors.append(f"gemini:{_mask(key)}={exc}")
                if _is_invalid_key(exc):
                    # Never retry a rejected credential on the request path.
                    invalid_keys += 1
                    with _lock:
                        _cooldown_until[key] = time.monotonic() + INVALID_KEY_COOLDOWN_SECONDS
                elif _is_retryable(exc):
                    with _lock:
                        _cooldown_until[key] = time.monotonic() + COOLDOWN_SECONDS
                continue
            with _lock:
                _next_index = (start + i + 1) % len(keys)
                _cooldown_until.pop(key, None)
            return text, f"gemini:{_mask(key)}"

    if prefer != "groq":
        try:
            return _call_groq(system, prompt, max_tokens), "groq"
        except Exception as exc:
            errors.append(f"groq={exc}")

    if errors:
        logger.warning("chat providers failed: %s", "; ".join(errors))

    groq_ready = settings.groq_configured
    if not keys and not groq_ready:
        raise LLMError(
            "The AI coach isn't configured yet. Add a valid GEMINI_API_KEY "
            "(or GROQ_API_KEY) to enable it."
        )
    if invalid_keys and invalid_keys >= len(keys) and not groq_ready:
        raise LLMError(
            "The AI coach's API key was rejected by the provider. Replace "
            "GEMINI_API_KEY with a valid key (or configure GROQ_API_KEY)."
        )
    if cooling_keys and cooling_keys >= len(keys) and not groq_ready:
        raise LLMError(UNAVAILABLE_MESSAGE)
    raise LLMError(UNAVAILABLE_MESSAGE)


def reset_state() -> None:
    """Test helper: clear rotation index + cooldowns."""
    global _next_index, _groq_cooldown_until
    with _lock:
        _next_index = 0
        _groq_cooldown_until = 0.0
        _cooldown_until.clear()
