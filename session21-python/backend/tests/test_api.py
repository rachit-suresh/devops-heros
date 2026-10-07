import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app

# NOTE (Rachit, 24BCS10139): the reference test built TestClient without the
# context manager, so the FastAPI startup hook (table creation) never ran and
# test_create_task_validation failed with "no such table: tasks". Using the
# context manager fires startup/shutdown events and fixes it.

@pytest.fixture(scope="module")
def client():
    if os.path.exists("test.db"):
        os.remove("test.db")
    with TestClient(app) as c:
        yield c

def test_health(client):
    assert client.get("/health").json() == {"status": "UP"}

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "TaskBoard API"

def test_create_task_validation(client):
    response = client.post("/api/tasks", json={"title": "Deploy application", "priority": "HIGH", "assignee": "Student"})
    assert response.status_code == 201
    assert response.json()["title"] == "Deploy application"
