from motor.motor_asyncio import AsyncIOMotorClient
import os


class WeatherRepository:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
        client = AsyncIOMotorClient(mongo_uri)
        self.db = client["weatherdb"]
        self.collection = self.db["weather_data"]

    async def get_latest_for_city(self, city: str, limit: int = 10):

    #Returneaza ultimele 10 inregistrari pentru un oras.

        cursor = (
            self.collection.find({"city": {"$regex": f"^{city}$", "$options": "i"}})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return [doc async for doc in cursor]

    async def insert_entry(self, entry: dict):

    #Insereaza o inregistrare noua in baza de date.

        await self.collection.insert_one(entry)
