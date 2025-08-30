

from fastapi import APIRouter

from .endpoints import login, users, businesses, categories, appointments, employees, reviews, chatbot, voice, search_assistant

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(search_assistant.router, prefix="/search", tags=["search"])
