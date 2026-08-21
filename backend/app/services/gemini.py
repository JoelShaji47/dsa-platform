import asyncio

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiError(Exception):
    pass


SYSTEM_INSTRUCTION = (
    "You are a DSA tutor for a gamified learning platform. "
    "Never reveal full solutions or complete working code. "
    "Guide the user with hints, intuition, complexity analysis, and "
    "point out flaws in their approach. Be concise and encouraging."
)


def _client() -> genai.Client:
    if not settings.gemini_configured:
        raise GeminiError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def model_name() -> str:
    return settings.GEMINI_MODEL


def generate_sync(
    prompt: str,
    system_instruction: str = SYSTEM_INSTRUCTION,
    json_mode: bool = False,
) -> str:
    client = _client()
    config_kwargs = {"system_instruction": system_instruction}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        if not response.text:
            raise GeminiError("Gemini returned an empty response")
        return response.text
    except GeminiError:
        raise
    except Exception as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc


async def generate(prompt: str, system_instruction: str = SYSTEM_INSTRUCTION) -> str:
    client = _client()

    def _call() -> str:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
        )
        if not response.text:
            raise GeminiError("Gemini returned an empty response")
        return response.text

    try:
        return await asyncio.to_thread(_call)
    except GeminiError:
        raise
    except Exception as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc
