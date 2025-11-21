from fastapi import APIRouter, HTTPException
from server.services.weather_service import WeatherService
import os

router = APIRouter()
service = WeatherService(api_key=os.getenv("OPENWEATHER_API_KEY"))

@router.get("/api/weather")
async def get_weather_data(city: str):

   #Endpoint async care interogheaza datele meteo pentru orasul cerut.

    try:
        return await service.get_weather_data(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
