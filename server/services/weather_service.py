import os
import requests
import grpc

from dotenv import load_dotenv
from server.api import weather_pb2, weather_pb2_grpc

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherService(weather_pb2_grpc.WeatherServiceServicer):
    def GetWeather(self, request, context):
        city = request.city

        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extragem datele din raspuns
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            return weather_pb2.WeatherResponse(
                city=city,
                temperature=temperature,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed
            )

        except requests.exceptions.HTTPError:
            context.abort(grpc.StatusCode.NOT_FOUND, f"City '{city}' not found.")
        except Exception:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to fetch weather data.")
