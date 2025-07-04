# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.database import Database
from controllers import enterprise
from bd.mono_client import get_database
from utils.responses import success_response

app = FastAPI(
    title="Booking and Store Service API",
    description="API para gestionar reservas y servicios de tiendas.",
    version="1.0.0",
)

app.include_router(enterprise.router, prefix="/api/v1")


@app.get(
    "/api/v1/health",
    summary="Verificar estado de la API y la base de datos",
    tags=["Health"]
)
def get_health_status(db: Database = Depends(get_database)):
    """
    Comprueba el estado de la conexión a la base de datos MongoDB.
    """
    try:
        db.command('ping')
        content = {"api_status": "ok", "database_status": "ok"}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"api_status": "ok", "database_status": "error", "reason": str(e)},
        )

@app.get("/", summary="Endpoint de Bienvenida", tags=["Root"])
def read_root():
    """
    Devuelve un mensaje de bienvenida para la API.
    """
    return success_response(data={"message": "Welcome to the Booking and Store Service API"})