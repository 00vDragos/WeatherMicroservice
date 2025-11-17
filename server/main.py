import os
import grpc
from dotenv import load_dotenv
from concurrent import futures

from server.api import weather_pb2_grpc
from server.services.weather_service import WeatherService  # urmează să-l implementăm


# Încarcă variabilele din fișierul .env
load_dotenv()
GRPC_API_KEY = os.getenv("GRPC_API_KEY")
PORT = 50051


# Interceptor pentru validarea cheii x-api-key
class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)
        if metadata.get("x-api-key") != GRPC_API_KEY:
            def deny_request(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing API key")
            return grpc.unary_unary_rpc_method_handler(deny_request)
        return continuation(handler_call_details)


def serve():
    # Inițializare server gRPC cu interceptor pentru autentificare
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(AuthInterceptor(),)
    )

    # Înregistrare serviciu WeatherService
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(
        WeatherService(), server
    )

    server.add_insecure_port(f"[::]:{PORT}")
    print(f"[gRPC server] Listening on port {PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
