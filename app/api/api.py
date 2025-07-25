
from fastapi import APIRouter
from .endpoints import login, users, businesses, categories, appointments

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])