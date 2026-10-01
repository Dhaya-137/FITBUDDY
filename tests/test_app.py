import os
from pathlib import Path
import tempfile


os.environ["DATABASE_URL"] = (
    "sqlite:///"
    + str(
        Path(tempfile.gettempdir())
        / "fitbuddy_test.db"
    )
)

os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.database import Base
from app.database import engine

from app.main import app


Base.metadata.drop_all(
    bind=engine
)

Base.metadata.create_all(
    bind=engine
)


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_api_get_missing_user():

    response = client.get(
        "/api/users/does-not-exist"
    )

    assert response.status_code == 404