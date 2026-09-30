import uuid
from collections import Counter

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_test_user
from app.seeds import PROBLEMS

client = TestClient(app)


def seed_counts():
    topics: Counter = Counter()
    difficulties: Counter = Counter()
    for p in PROBLEMS:
        topics[p["topic"]] += 1
        difficulties[p["difficulty"]] += 1
    return topics, difficulties


def make_user_and_token():
    headers, _ = make_test_user()
    return headers


def test_problems_require_auth():
    assert client.get("/api/v1/problems").status_code == 401
    res = client.get("/api/v1/problems/two-sum")
    assert res.status_code == 401


def test_list_returns_all_seeded_problems():
    headers = make_user_and_token()
    res = client.get("/api/v1/problems", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body) >= 149
    for item in body:
        assert set(item.keys()) == {"id", "title", "slug", "difficulty", "topic", "solved", "solvable", "sources", "pattern_key"}
        assert item["solved"] is False
        assert isinstance(item["solvable"], bool)


def test_list_solvable_matches_detail():
    headers = make_user_and_token()
    items = client.get("/api/v1/problems", headers=headers).json()
    assert any(item["solvable"] for item in items)
    assert any(not item["solvable"] for item in items)

    for item in items[::37]:
        detail = client.get(f"/api/v1/problems/{item['slug']}", headers=headers).json()
        assert item["solvable"] == detail["solvable"], item["slug"]


def test_filters_by_topic_difficulty_and_search():
    headers = make_user_and_token()

    arrays = client.get(
        "/api/v1/problems", params={"topic": "ARRAY"}, headers=headers
    ).json()
    assert len(arrays) >= 50
    assert all(item["topic"] == "ARRAY" for item in arrays)

    easy_arrays = client.get(
        "/api/v1/problems",
        params={"topic": "ARRAY", "difficulty": "EASY"},
        headers=headers,
    ).json()
    assert len(easy_arrays) >= 10
    assert all(item["topic"] == "ARRAY" and item["difficulty"] == "EASY" for item in easy_arrays)

    hits = client.get(
        "/api/v1/problems", params={"search": "anagram"}, headers=headers
    ).json()
    assert {item["slug"] for item in hits} == {"valid-anagram", "group-anagrams"}

    invalid = client.get(
        "/api/v1/problems", params={"topic": "NOPE"}, headers=headers
    )
    assert invalid.status_code == 422


def test_detail_strips_hidden_tests():
    headers = make_user_and_token()
    res = client.get("/api/v1/problems/two-sum", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Two Sum"
    assert body["starter_code"]["python"].startswith("import sys")
    visible = body["test_cases"]
    assert len(visible) == 3
    assert visible[0]["input"] == "4\n2 7 11 15\n9\n"
    assert visible[0]["expected_output"] == "0 1"
    for case in visible:
        assert "is_hidden" not in case


def test_detail_404_for_unknown_slug():
    headers = make_user_and_token()
    res = client.get("/api/v1/problems/does-not-exist", headers=headers)
    assert res.status_code == 404


def test_topic_counts_match_seed_plan():
    headers = make_user_and_token()
    problems = client.get("/api/v1/problems", headers=headers).json()
    counts: dict[str, int] = {}
    difficulties: dict[str, int] = {}
    for item in problems:
        counts[item["topic"]] = counts.get(item["topic"], 0) + 1
        difficulties[item["difficulty"]] = difficulties.get(item["difficulty"], 0) + 1

    # DB must mirror the seed catalog exactly (counts grow with the catalog:
    # NeetCode 250 delta, TUF A2Z, ...). Authored sources win on overlap
    # (deduped by slug in app/seeds/__init__.py).
    expected_topics, expected_difficulties = seed_counts()
    assert counts == dict(expected_topics)
    assert sum(counts.values()) == len(PROBLEMS)
    assert difficulties == dict(expected_difficulties)
    assert difficulties["HARD"] >= 20
