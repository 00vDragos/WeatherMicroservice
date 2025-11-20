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

        print(f" Fetching weather for city: {city}")
        print(f" API key: {OPENWEATHER_API_KEY}")
        print(f"URL: {url}")

        try:
            response = requests.get(url)
            print(f" Raw response object: {response}")
            print(f" Status code: {response.status_code}")

            response.raise_for_status()  # va genera HTTPError pentru coduri 4xx/5xx

            print(" Status OK. Parsing JSON...")
            data = response.json()
            print(f"OpenWeatherMap raw response: {data}")

            # Extragem datele
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            print(f"Extracted data-> temp: {temperature}, humidity: {humidity}, desc: {description}, wind: {wind_speed}")

            # Salvăm în MongoDB
            self.repo.save_weather_data(
                city=city,
                temperature=temperature,
                humidity=humidity,
                description=description,
                wind_speed=wind_speed
            )

            print("Weather data saved in MongoDB.")

            return weather_pb2.WeatherResponse(
                city=city,
                temperature=temperature,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed
            )

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"City '{city}' not found or invalid response.")

        except requests.exceptions.RequestException as req_err:
            print(f"Network-related error: {req_err}")
            context.abort(grpc.StatusCode.UNAVAILABLE, "Weather service is currently unreachable.")

        except Exception as e:
            print(f"Unexpected error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error while fetching weather data.")