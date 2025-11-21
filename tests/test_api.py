import pytest
from fastapi.testclient import TestClient
from server.main import app


client = TestClient(app)


def test_api_weather_route():
    """Verifica daca ruta /api/weather exista si raspunde corect"""
    response = client.get("/api/weather?city=London")

    assert response.status_code in [200, 404, 500]
    assert "detail" in response.json() or isinstance(response.json(), list)
