from dotenv import load_dotenv
import os
import sys
from fastapi.testclient import TestClient

# Mock OpenAI API Key for the test so it doesn't fail initialization
#os.environ["OPENAI_API_KEY"] = "sk-dummy-key"
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Add backend directory to path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Vel-Kural API" in response.json()["message"]

def test_generate_story_invalid_kural():
    # Test valid payload but invalid kural number out of bounds
    response = client.post(
        "/generate_story",
        json={"kural_number": 9999}
    )
    # The API throws a 404 for an out-of-bounds kural
    assert response.status_code == 404
    assert "Kural not found" in response.json()["detail"]

def test_generate_story_invalid_payload():
    # Test completely missing or invalid payload
    response = client.post(
        "/generate_story",
        json={"wrong_field": "test"}
    )
    # Pydantic validation should return 422 Unprocessable Entity
    assert response.status_code == 422

# NOTE: We do not typically unit-test the actual OpenAI generation 
# unless we mock the OpenAI API, to save costs and run tests deterministically.