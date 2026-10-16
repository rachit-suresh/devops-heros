import pytest

ALBUM = {"title": "OK Computer", "artist": "Radiohead", "year": 1997}

def create(client):
    response = client.post("/api/albums", json=ALBUM)
    assert response.status_code == 201
    return response.json()["id"]

def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "app": "tracktonic"}

def test_ready(client):
    assert client.get("/ready").status_code == 200

def test_create_album(client):
    album_id = create(client)
    result = client.get(f"/api/albums/{album_id}").json()
    assert result["title"] == ALBUM["title"]
    assert result["status"] == "queued"

def test_empty_list(client):
    assert client.get("/api/albums").json() == []

def test_list_and_filter(client):
    album_id = create(client)
    client.put(f"/api/albums/{album_id}", json={"status": "listening"})
    assert len(client.get("/api/albums?status=listening").json()) == 1
    assert client.get("/api/albums?status=queued").json() == []

def test_rating_marks_listened(client):
    album_id = create(client)
    response = client.put(f"/api/albums/{album_id}", json={"rating": 5})
    assert response.status_code == 200
    assert response.json()["rating"] == 5
    assert response.json()["status"] == "listened"

@pytest.mark.parametrize("payload", [{"rating": 0}, {"rating": 6}, {"status": "unknown"}])
def test_invalid_update(client, payload):
    album_id = create(client)
    assert client.put(f"/api/albums/{album_id}", json=payload).status_code == 422

@pytest.mark.parametrize("payload", [{"title": " ", "artist": "A"}, {"title": "A", "artist": ""}, {**ALBUM, "year": 999}])
def test_invalid_create(client, payload):
    assert client.post("/api/albums", json=payload).status_code == 422

def test_delete(client):
    album_id = create(client)
    assert client.delete(f"/api/albums/{album_id}").status_code == 204
    assert client.get(f"/api/albums/{album_id}").status_code == 404

@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_not_found(client, method):
    kwargs = {"json": {"rating": 3}} if method == "put" else {}
    assert getattr(client, method)("/api/albums/99999", **kwargs).status_code == 404

def test_strip_whitespace(client):
    response = client.post("/api/albums", json={"title": " Discovery ", "artist": " Daft Punk "})
    assert response.json()["title"] == "Discovery"

def test_metrics(client):
    create(client)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "tracktonic_http_requests_total" in response.text
    assert "/api/albums" in response.text
