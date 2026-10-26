"""Route-level checks: status code and response structure only.

Input validation belongs in tests/unit/test_models.py.
"""

LINK_KEYS = {"code", "url", "clicks"}


def assert_link_shape(body):
    assert set(body) == LINK_KEYS
    assert isinstance(body["code"], str)
    assert isinstance(body["url"], str)
    assert isinstance(body["clicks"], int)


def create(client, url="https://example.com"):
    return client.post("/api/links", json={"url": url})


# POST /api/links


def test_create_returns_201_with_a_link(client):
    response = create(client)

    assert response.status_code == 201
    assert_link_shape(response.json())


# GET /api/links


def test_list_returns_200_and_an_empty_list_when_there_are_no_links(client):
    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_200_and_a_list_of_links(client):
    create(client, "https://a.example")
    create(client, "https://b.example")

    response = client.get("/api/links")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    for item in body:
        assert_link_shape(item)


# GET /api/links/{code}/stats


def test_stats_returns_200_with_a_link(client):
    code = create(client).json()["code"]

    response = client.get(f"/api/links/{code}/stats")

    assert response.status_code == 200
    assert_link_shape(response.json())


def test_stats_for_an_unknown_code_returns_404_with_a_detail(client):
    response = client.get("/api/links/nope00/stats")

    assert response.status_code == 404
    assert set(response.json()) == {"detail"}


# GET /{code}


def test_follow_returns_a_307_redirect_with_a_location_header(client):
    code = create(client).json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert "location" in response.headers


def test_follow_an_unknown_code_returns_404_with_a_detail(client):
    response = client.get("/nope00", follow_redirects=False)

    assert response.status_code == 404
    assert set(response.json()) == {"detail"}
