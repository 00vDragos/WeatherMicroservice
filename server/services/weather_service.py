from datetime import datetime, timezone
import httpx
from server.repositories.weather_repository import WeatherRepository


class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.repo = WeatherRepository()

    async def get_weather_data(self, city: str):

       #Cauta in baza de date datele orasului cerut, daca nu exista apeleaza OpenWeatherMap


        data = await self.repo.get_latest_for_city(city)

        if data:
            return [
                {
                    "timestamp": entry.get("timestamp").isoformat() if entry.get("timestamp") else None,
                    "city": entry.get("city"),
                    "temperature": entry.get("temperature"),
                    "humidity": entry.get("humidity"),
                    "description": entry.get("description"),
                    "wind_speed": entry.get("wind_speed"),
                }
                for entry in reversed(data)
            ]

        #Daca nu exista in DB -> apelam OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise ValueError(f"City not found or API error: {response.status_code}")

        weather_data = response.json()
        entry = {
            "timestamp": datetime.now(timezone.utc),
            "city": weather_data.get("name", city),
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"],
        }

        await self.repo.insert_entry(entry)
        return [entry]
