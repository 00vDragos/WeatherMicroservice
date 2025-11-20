import os
import grpc
from dotenv import load_dotenv
from concurrent import futures
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from api import weather_pb2, weather_pb2_grpc
from services.weather_service import WeatherService
from api.rest_api import router as rest_router

# Incarcare variabile .env
load_dotenv()
GRPC_API_KEY = os.getenv("GRPC_API_KEY")
PORT = 50051

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_app")

# Interceptor pentru x-api-key
class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)
        if metadata.get("x-api-key") != GRPC_API_KEY:
            def deny_request(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing API key")
            return grpc.unary_unary_rpc_method_handler(deny_request)
        return continuation(handler_call_details)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(AuthInterceptor(),)
    )
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(GRPC_API_KEY), server)
    server.add_insecure_port(f"[::]:{PORT}")
    logger.info(f"[gRPC server] Listening on port {PORT}")
    server.start()
    server.wait_for_termination()

# FastAPI app
app = FastAPI()
app.include_router(rest_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
