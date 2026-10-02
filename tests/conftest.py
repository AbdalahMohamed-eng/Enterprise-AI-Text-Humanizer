import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_nlp_text():
    """Returns some standard text for NLP testing."""
    return "It is important to remember that we must delve into this myriad of transformative issues to truly navigate the landscape."
