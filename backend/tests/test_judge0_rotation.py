"""RapidAPI key rotation for the Judge0 service (one building block at a time)."""

import asyncio

import httpx
import pytest

from app.core.config import settings
from app.services import judge0
from app.services.judge0 import Judge0Error

SCRIPT: list = []


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {"status": {"id": 3}}
        self.text = f"fake {status_code}"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"fake {self.status_code}",
                request=None,  # type: ignore[arg-type]
                response=self,  # type: ignore[arg-type]
            )

    def json(self):
        return dict(self._payload)


class _FakeClient:
    """Replays SCRIPT, recording headers per attempt."""

    instances: list["_FakeClient"] = []

    def __init__(self, *args, **kwargs):
        self.headers_seen: list[dict] = []
        _FakeClient.instances.append(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json=None, params=None, headers=None):
        self.headers_seen.append(dict(headers or {}))
        item = SCRIPT.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    SCRIPT.clear()
    _FakeClient.instances.clear()
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: _FakeClient(*a, **k))
    monkeypatch.setattr(settings, "JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
    monkeypatch.setattr(settings, "JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")
    monkeypatch.setattr(settings, "JUDGE0_API_KEY", "")
    monkeypatch.setattr(settings, "JUDGE0_API_KEYS", "")
    for i in range(1, 31):
        monkeypatch.delenv(f"JUDGE0_API_KEY{i}", raising=False)
        monkeypatch.setattr(settings, f"JUDGE0_API_KEY{i}", "")
    yield


def test_no_keys_sends_no_rapidapi_headers():
    SCRIPT.append(_FakeResponse(200))
    out = asyncio.run(judge0.submit("print(1)", "python"))
    assert out["status_key"] == "ACCEPTED"
    assert _FakeClient.instances[0].headers_seen == [{}]


def test_quota_error_rotates_to_next_key(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE0_API_KEYS", "spent-key,live-key")
    SCRIPT.extend([_FakeResponse(429), _FakeResponse(200)])
    out = asyncio.run(judge0.submit("print(1)", "python"))
    assert out["status_key"] == "ACCEPTED"
    seen = _FakeClient.instances[0].headers_seen
    assert [h.get("X-RapidAPI-Key") for h in seen] == ["spent-key", "live-key"]


def test_all_keys_spent_raises(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE0_API_KEYS", "k1,k2")
    SCRIPT.extend([_FakeResponse(429), _FakeResponse(429)])
    with pytest.raises(Judge0Error, match="429"):
        asyncio.run(judge0.submit("print(1)", "python"))


def test_bad_submission_does_not_burn_keys(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE0_API_KEYS", "k1,k2")
    SCRIPT.append(_FakeResponse(422))
    with pytest.raises(Judge0Error, match="422"):
        asyncio.run(judge0.submit("print(1)", "python"))
    assert len(_FakeClient.instances[0].headers_seen) == 1


def test_numbered_env_keys_are_honored(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE0_API_KEY1", "n1")
    monkeypatch.setattr(settings, "JUDGE0_API_KEY2", "n1")  # duplicate collapses
    monkeypatch.setattr(settings, "JUDGE0_API_KEY3", "n3")
    assert settings.judge0_keys == ["n1", "n3"]


def test_single_key_fallback(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE0_API_KEY", "solo")
    assert settings.judge0_keys == ["solo"]
