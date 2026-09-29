import httpx

from app.core.config import settings

LANGUAGE_IDS = {
    "python": 71,
    "cpp": 54,
    "java": 62,
}

MEMORY_LIMITS_KB = {
    "python": 256000,
    "cpp": 256000,
    "java": 4096000,
}

STATUS_CODES = {
    1: "IN_QUEUE",
    2: "PROCESSING",
    3: "ACCEPTED",
    4: "WRONG_ANSWER",
    5: "TIME_LIMIT_EXCEEDED",
    6: "COMPILATION_ERROR",
    7: "RUNTIME_ERROR_SIGSEGV",
    8: "RUNTIME_ERROR_SIGXFSZ",
    9: "RUNTIME_ERROR_SIGFPE",
    10: "RUNTIME_ERROR_SIGABRT",
    11: "RUNTIME_ERROR_UNKNOWN",
    12: "INTERNAL_ERROR",
    13: "EXEC_FORMAT_ERROR",
}


class Judge0Error(Exception):
    pass


def _headers() -> dict[str, str]:
    if not settings.JUDGE0_API_KEY:
        return {}
    return {
        "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        "X-RapidAPI-Host": settings.JUDGE0_API_HOST,
    }


def _base_url() -> str:
    if not settings.judge0_configured:
        raise Judge0Error("JUDGE0_API_URL is not configured")
    return settings.JUDGE0_API_URL.rstrip("/")


async def submit(source_code: str, language: str, stdin: str = "") -> dict:
    language_id = LANGUAGE_IDS.get(language)
    if language_id is None:
        raise Judge0Error(f"Unsupported language: {language}")

    url = f"{_base_url()}/submissions"
    params = {"base64_encoded": "false", "wait": "true"}
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "cpu_time_limit": 5,
        "memory_limit": MEMORY_LIMITS_KB.get(language, 256000),
        # macOS/Rosetta host: per-process limits MUST stay False — isolate's
        # per-process sandboxing mmaps fail under Rosetta (status 12/13).
        # Only flip to True on a Windows/WSL2 (cgroup v2) host.
        "enable_per_process_and_thread_time_limit": False,
        "enable_per_process_and_thread_memory_limit": False,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                url, json=payload, params=params, headers=_headers()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise Judge0Error(
                f"Judge0 returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise Judge0Error(f"Could not reach Judge0: {exc}") from exc

    result = response.json()
    status_id = result.get("status", {}).get("id")
    result["status_key"] = STATUS_CODES.get(status_id, "UNKNOWN")
    return result
