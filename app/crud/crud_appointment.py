from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timedelta

async def create(db: AsyncIOMotorDatabase, *, business_id: str, user_id: str, appointment_time: datetime):
    """Crea un nuevo documento de cita en la base de datos."""
    appointment_doc = {
        "business_id": ObjectId(business_id),
        "user_id": ObjectId(user_id),
        "appointment_time": appointment_time,
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }
    
    result = await db["appointments"].insert_one(appointment_doc)
    created_appointment = await db["appointments"].find_one({"_id": result.inserted_id})
    return created_appointment