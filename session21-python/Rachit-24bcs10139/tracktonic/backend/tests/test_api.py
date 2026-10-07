import os
os.environ["DATABASE_URL"] = "sqlite:///./test_tracktonic.db"

from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_album():
    r = client.post("/api/albums", json={"title": "OK Computer", "artist": "Radiohead", "year": 1997})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "queued"
    assert body["id"] >= 1

def test_list_albums():
    client.post("/api/albums", json={"title": "Discovery", "artist": "Daft Punk", "year": 2001})
    r = client.get("/api/albums")
    assert r.status_code == 200
    assert len(r.json()) >= 2

def test_get_album_by_id():
    r = client.get("/api/albums/1")
    assert r.status_code == 200
    assert r.json()["title"] == "OK Computer"

def test_rate_album_marks_listened():
    r = client.put("/api/albums/1", json={"rating": 5})
    assert r.status_code == 200
    assert r.json()["rating"] == 5
    assert r.json()["status"] == "listened"

def test_update_validation_rejects_bad_rating():
    r = client.put("/api/albums/1", json={"rating": 9})
    assert r.status_code == 422

def test_delete_album():
    r = client.delete("/api/albums/2")
    assert r.status_code == 204
    assert client.get("/api/albums/2").status_code == 404

def test_metrics_endpoint_prometheus_format():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "tracktonic_http_requests_total" in r.text
