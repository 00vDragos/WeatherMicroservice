import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from server.services.weather_service import WeatherService


@pytest_asyncio.fixture
async def service():
    return WeatherService(api_key="dummy_key")


@pytest.mark.asyncio
@patch("server.services.weather_service.httpx.AsyncClient.get")
async def test_get_weather_data_from_api(mock_get, service):
    """Test pentru apelul OpenWeatherMap cand nu exista date in DB"""
    # Mock HTTP response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "name": "London",
        "main": {"temp": 18.5, "humidity": 82},
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 4.5}
    }

    mock_get.return_value = mock_response

    # Mock DB repository
    service.repo.get_latest_for_city = AsyncMock(return_value=[])
    service.repo.insert_entry = AsyncMock()

    result = await service.get_weather_data("London")

    assert len(result) == 1
    assert result[0]["city"] == "London"
    assert "temperature" in result[0]
    service.repo.insert_entry.assert_called_once()
