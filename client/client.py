import grpc
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.api import weather_pb2, weather_pb2_grpc

load_dotenv()

GRPC_API_KEY = os.getenv("GRPC_API_KEY")
CHANNEL = "localhost:50051"


def main():
    with grpc.insecure_channel(CHANNEL) as channel:
        stub = weather_pb2_grpc.WeatherServiceStub(channel)

        city = input("Enter city name: ").strip()

        try:
            response = stub.GetWeather(
                weather_pb2.WeatherRequest(city=city),
                metadata=[("x-api-key", GRPC_API_KEY)]
            )

            print(f"\nWeather for {response.city}:")
            print(f"Temperature: {response.temperature:.1f} °C")
            print(f"Humidity: {response.humidity}%")
            print(f"Conditions: {response.description}")
            print(f"Wind Speed: {response.wind_speed} m/s")

        except grpc.RpcError as e:
            print(f"\n❌ Error: {e.code().name} - {e.details()}")


if __name__ == "__main__":
    main()
