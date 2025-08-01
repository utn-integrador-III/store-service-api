
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.service import ServiceBase 
from bson import ObjectId 

async def get_services(db: AsyncIOMotorDatabase):
    services = await db["services"].find().to_list(100)
    return services

async def create_service(db: AsyncIOMotorDatabase, service: ServiceBase):
    service_data = service.model_dump()
    result = await db["services"].insert_one(service_data)
    created_service = await db["services"].find_one({"_id": result.inserted_id})
    return created_service

async def update_service(db: AsyncIOMotorDatabase, service_id: str, service_in: ServiceBase):
    object_id = ObjectId(service_id) 
    update_data = service_in.model_dump(exclude_unset=True) 
    
    if not update_data: 
        return await db["services"].find_one({"_id": object_id})

    await db["services"].update_one({"_id": object_id}, {"$set": update_data})
    return await db["services"].find_one({"_id": object_id})

async def delete_service(db: AsyncIOMotorDatabase, service_id: str):
    object_id = ObjectId(service_id) 
    result = await db["services"].delete_one({"_id": object_id})
    return result 