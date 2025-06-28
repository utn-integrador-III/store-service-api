from fastapi import FastAPI
from utils.responses import success_response

app = FastAPI(
    title="Booking and Store Service API",
    description="API for managing business Booking and Store Service.",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return success_response(data={"message": "Welcome to the Booking and Store Service API"})