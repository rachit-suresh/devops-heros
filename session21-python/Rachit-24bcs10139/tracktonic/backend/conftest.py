import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Isolated database file; never use the deployment database for unit tests.
_test_dir = tempfile.TemporaryDirectory(prefix="tracktonic-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_dir.name) / "test.db")
from app.database import Base, engine
from app.main import app

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
