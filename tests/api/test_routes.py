"""Integration/API tests for snip's HTTP routes, via FastAPI's TestClient.

Status code and response structure only — request-body validation cases
(SLI 4) belong in tests/unit/test_models.py, not here.
"""

import pytest
from fastapi.testclient import TestClient

from snip.main import app
from snip.store import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_store():
    """store is a module-level singleton shared across tests; reset it so
    tests don't see each other's records."""
    store._links.clear()
    yield
    store._links.clear()


def _create(url: str = "https://example.com/target") -> dict:
    return client.post("/api/links", json={"url": url}).json()


# --- POST /api/links -------------------------------------------------------

def test_create_link_returns_201_with_link_response():
    response = client.post("/api/links", json={"url": "https://example.com/target"})

    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) == {"code", "url", "clicks"}
    assert isinstance(body["code"], str) and body["code"]
    assert body["url"] == "https://example.com/target"
    assert body["clicks"] == 0


# --- GET /api/links ----------------------------------------------------------

def test_list_links_returns_200_with_a_list_of_link_responses():
    _create()

    response = client.get("/api/links")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert set(body[0].keys()) == {"code", "url", "clicks"}


# --- GET /api/links/{code}/stats ---------------------------------------------

def test_link_stats_returns_200_with_link_response_for_known_code():
    created = _create()

    response = client.get(f"/api/links/{created['code']}/stats")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"code", "url", "clicks"}
    assert body["code"] == created["code"]


def test_link_stats_returns_404_for_unknown_code():
    response = client.get("/api/links/doesnotexist/stats")

    assert response.status_code == 404
    assert "detail" in response.json()


# --- GET /{code} (follow) -----------------------------------------------------

def test_follow_redirects_307_to_the_stored_url():
    created = _create()

    response = client.get(f"/{created['code']}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/target"


def test_follow_returns_404_for_unknown_code():
    response = client.get("/doesnotexist", follow_redirects=False)

    assert response.status_code == 404
    assert "detail" in response.json()
