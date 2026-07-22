import os
import sys

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

# None of these tests call the OpenAI API, so they must not require a real key.
# Locally .env supplies one; CI sets a dummy value. Tests that do hit the API
# belong in a separate, scheduled eval workflow.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")

# Add backend directory to path so we can import the app package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Vel-Kural API" in response.json()["message"]


@pytest.mark.xfail(reason="/generate_story is not implemented yet", strict=True)
def test_generate_story_invalid_kural():
    # Test valid payload but invalid kural number out of bounds
    response = client.post(
        "/generate_story",
        json={"kural_number": 9999}
    )
    # The API throws a 404 for an out-of-bounds kural
    assert response.status_code == 404
    assert "Kural not found" in response.json()["detail"]


@pytest.mark.xfail(reason="/generate_story is not implemented yet", strict=True)
def test_generate_story_invalid_payload():
    # Test completely missing or invalid payload
    response = client.post(
        "/generate_story",
        json={"wrong_field": "test"}
    )
    # Pydantic validation should return 422 Unprocessable Entity
    assert response.status_code == 422
