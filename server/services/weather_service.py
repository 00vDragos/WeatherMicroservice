import os
import requests
import grpc
from dotenv import load_dotenv

from server.api import weather_pb2, weather_pb2_grpc
from server.repositories.weather_repository import WeatherRepository

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherService(weather_pb2_grpc.WeatherServiceServicer):
    def __init__(self):
        self.repo = WeatherRepository()

    def GetWeather(self, request, context):
        city = request.city

        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        print(f"[DEBUG] Fetching weather for city: {city}")
        print(f"[DEBUG] API key: {OPENWEATHER_API_KEY}")
        print(f"[DEBUG] URL: {url}")

        try:
            response = requests.get(url)
            print(f"[DEBUG] Raw response object: {response}")
            print(f"[DEBUG] Status code: {response.status_code}")

            response.raise_for_status()  # va genera HTTPError pentru coduri 4xx/5xx

            print("[DEBUG] Status OK. Parsing JSON...")
            data = response.json()
            print(f"[DEBUG] OpenWeatherMap raw response: {data}")

            # Extragem datele
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            print(f"[DEBUG] Extracted data → temp: {temperature}, humidity: {humidity}, desc: {description}, wind: {wind_speed}")

            # Salvăm în MongoDB
            self.repo.save_weather_data(
                city=city,
                temperature=temperature,
                humidity=humidity,
                description=description,
                wind_speed=wind_speed
            )

            print("[DEBUG] Weather data saved in MongoDB.")

            return weather_pb2.WeatherResponse(
                city=city,
                temperature=temperature,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed
            )

        except requests.exceptions.HTTPError as http_err:
            print(f"[ERROR] HTTP error occurred: {http_err}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"City '{city}' not found or invalid response.")

        except requests.exceptions.RequestException as req_err:
            print(f"[ERROR] Network-related error: {req_err}")
            context.abort(grpc.StatusCode.UNAVAILABLE, "Weather service is currently unreachable.")

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error while fetching weather data.")