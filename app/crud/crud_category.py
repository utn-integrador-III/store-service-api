
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.category import CategoryCreate

async def create_category(db: AsyncIOMotorDatabase, category: CategoryCreate):
    category_data = category.model_dump()
    result = await db["categories"].insert_one(category_data)
    return await db["categories"].find_one({"_id": result.inserted_id})

async def get_category_by_name(db: AsyncIOMotorDatabase, name: str):
    return await db["categories"].find_one({"name": name})

async def get_all_categories(db: AsyncIOMotorDatabase):
    return await db["categories"].find().to_list(100)