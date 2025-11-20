from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from datetime import datetime, timezone
import requests
import os

router = APIRouter()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["weatherdb"]
collection = db["weather_data"]

API_KEY = os.getenv("OPENWEATHER_API_KEY")

@router.get("/api/weather")
def get_weather_data(city: str):
    try:
        data = list(
            collection.find({"city": {"$regex": f"^{city}$", "$options": "i"}})
            .sort("timestamp", -1)
            .limit(10)
        )

        if data:
            result = [
                {
                    "timestamp": entry.get("timestamp").isoformat() if entry.get("timestamp") else None,
                    "city": entry.get("city"),
                    "temperature": entry.get("temperature"),
                    "humidity": entry.get("humidity"),
                    "description": entry.get("description"),
                    "wind_speed": entry.get("wind_speed"),
                }
                for entry in data
            ][::-1]
            return result

        # --- Dacă nu există în DB, apelăm API-ul extern ---
        if not API_KEY:
            raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY")

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        weather_data = response.json()

        # Dacă API-ul nu găsește orașul
        if response.status_code != 200 or "main" not in weather_data:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")

        entry = {
            "timestamp": datetime.now(timezone.utc),
            "city": weather_data.get("name", city),
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"],
        }

        # Salvăm imediat și returnăm (fără 404)
        collection.insert_one(entry)
        return [entry]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
