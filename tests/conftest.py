import sys
from pathlib import Path

# Add the src directory to the path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """Fixture to get the current activities state."""
    response = client.get("/activities")
    return response.json()
