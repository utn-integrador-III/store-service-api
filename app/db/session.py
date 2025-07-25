from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class DataBase:
    client: AsyncIOMotorClient = None

db = DataBase()

async def get_database() -> AsyncIOMotorClient:
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    print("Conectando a MongoDB Atlas...")
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)
    print("¡Conexión a MongoDB Atlas exitosa!")

async def close_mongo_connection():
    print("Cerrando la conexión a MongoDB...")
    db.client.close()
    print("¡Conexión cerrada!")