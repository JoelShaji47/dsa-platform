import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_user_and_token():
    suffix = uuid.uuid4().hex[:8]
    data = {
        "username": f"user_{suffix}",
        "email": f"{suffix}@test.com",
        "password": "supersecret1",
    }
    client.post("/api/v1/auth/register", json=data)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": data["email"], "password": data["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_problems_require_auth():
    assert client.get("/api/v1/problems").status_code == 401
    res = client.get("/api/v1/problems/two-sum")
    assert res.status_code == 401


def test_list_returns_all_seeded_problems():
    headers = make_user_and_token()
    res = client.get("/api/v1/problems", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body) >= 34
    for item in body:
        assert set(item.keys()) == {"id", "title", "slug", "difficulty", "topic", "solved"}
        assert item["solved"] is False


def test_filters_by_topic_difficulty_and_search():
    headers = make_user_and_token()

    arrays = client.get(
        "/api/v1/problems", params={"topic": "ARRAY"}, headers=headers
    ).json()
    assert len(arrays) == 6
    assert all(item["topic"] == "ARRAY" for item in arrays)

    easy_arrays = client.get(
        "/api/v1/problems",
        params={"topic": "ARRAY", "difficulty": "EASY"},
        headers=headers,
    ).json()
    assert len(easy_arrays) == 2
    assert all(item["difficulty"] == "EASY" for item in easy_arrays)

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
    assert len(visible) == 2
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
    assert counts == {
        "ARRAY": 6,
        "STRING": 5,
        "LINKED_LIST": 4,
        "STACK": 3,
        "QUEUE": 1,
        "TREE": 6,
        "GRAPH": 3,
        "DP": 6,
    }
    assert difficulties["HARD"] == 4
