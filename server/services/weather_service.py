"""import os
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
            response.raise_for_status()
            data = response.json()

            # Extragem datele
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            # Salvăm în MongoDB
            self.repo.save_weather_data(
                city=city,
                temperature=temperature,
                humidity=humidity,
                description=description,
                wind_speed=wind_speed
            )

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
            context.abort(grpc.StatusCode.INTERNAL, "Failed to fetch weather data.") """

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

        # DEBUG: Verificare URL și API key
        print(f"[DEBUG] Fetching weather for city: {city}")
        print(f"[DEBUG] API key: {OPENWEATHER_API_KEY}")
        print(f"[DEBUG] URL: {url}")

        try:
            response = requests.get(url)

            # DEBUG: Răspuns brut
            print(f"[DEBUG] Raw response object: {response}")
            print(f"[DEBUG] Status code: {response.status_code}")

            response.raise_for_status()

            print("[DEBUG] Status OK. Parsing JSON...")

            data = response.json()

            # DEBUG: Răspuns JSON complet
            print(f"[DEBUG] OpenWeatherMap raw response: {data}")

            # Extragem datele
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            # DEBUG: Date extrase
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

        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] HTTPError: {e}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"City '{city}' not found.")
        except Exception as e:
            print(f"[ERROR] Unexpected exception: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Failed to fetch weather data.")
