"""Chat LLM provider: Gemini key rotation with Groq fallback.

Additive only — hints/reviews keep using ``app.services.gemini`` directly.
This module serves the interactive Solve-page coach, where bursty per-user
traffic can exhaust a single Gemini key.

Order: Gemini keys round-robin (per-key 60s cooldown on 429/5xx/quota)
→ Groq (OpenAI-compatible) → raise LLMError (mapped to 503).
"""

import threading
import time

import httpx
from google import genai
from google.genai import types

from app.core.config import settings

COOLDOWN_SECONDS = 60.0
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMError(Exception):
    pass


_lock = threading.Lock()
_next_index = 0
_cooldown_until: dict[str, float] = {}


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
        ),
    )
    if not response.text:
        raise LLMError("Gemini returned an empty response")
    return response.text


def _call_groq(system: str, prompt: str, max_tokens: int = 700) -> str:
    if not settings.groq_configured:
        raise LLMError("Groq is not configured")
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
    if resp.status_code == 429:
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
    429/5xx/quota) → Groq → error. prefer="groq" flips the order for
    bulk/background workloads where Groq throughput matters more.
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

    if prefer != "groq":
        errors = []
    if keys:
        for i in range(len(keys)):
            key = keys[(start + i) % len(keys)]
            if _cooldown_until.get(key, 0) > now:
                errors.append(f"gemini:{_mask(key)}=cooldown")
                continue
            try:
                text = _call_gemini(key, system, prompt, max_tokens)
            except Exception as exc:
                errors.append(f"gemini:{_mask(key)}={exc}")
                if _is_retryable(exc if isinstance(exc, Exception) else Exception(str(exc))):
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
        except LLMError as exc:
            errors.append(f"groq={exc}")
        except Exception as exc:
            errors.append(f"groq={exc}")

    raise LLMError("All chat providers failed: " + "; ".join(errors) if errors else "No chat provider configured")


def reset_state() -> None:
    """Test helper: clear rotation index + cooldowns."""
    global _next_index
    with _lock:
        _next_index = 0
        _cooldown_until.clear()
