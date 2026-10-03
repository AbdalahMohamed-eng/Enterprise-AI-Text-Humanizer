def test_get_root(client):
    """Test GET / returns 200 and HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_models(client):
    """Test GET /api/v1/models returns 200 and the list of providers."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "openai" in data
    assert isinstance(data["openai"], list)


def test_humanize_invalid_input(client):
    """Test POST /api/v1/humanize with invalid inputs (text too short) returns 422."""
    payload = {
        "text": "short",  # Text must be at least 10 characters
        "provider": "groq",
        "model": "groq/llama-3.3-70b-versatile",
    }
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["type"] == "string_too_short"
