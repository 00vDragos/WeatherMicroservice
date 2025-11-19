import os
from datetime import datetime, UTC
from pymongo import MongoClient
from dotenv import load_dotenv



load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "weatherdb"
COLLECTION_NAME = "weather_data"


class WeatherRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    def save_weather_data(self, city: str, temperature: float, humidity: int, description: str, wind_speed: float):
        document = {
            "city": city,
            "temperature": temperature,
            "humidity": humidity,
            "description": description,
            "wind_speed": wind_speed,
            "timestamp": datetime.now(UTC)
        }

        result = self.collection.insert_one(document)
        return str(result.inserted_id)
