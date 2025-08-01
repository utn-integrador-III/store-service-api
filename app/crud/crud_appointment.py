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

async def get_appointments_by_user_id(db: AsyncIOMotorDatabase, user_id: str):
    """Obtiene todas las citas de un usuario específico."""
    return await db["appointments"].find({"user_id": ObjectId(user_id)}).to_list(100)

async def get_appointments_by_business_id_and_date(db: AsyncIOMotorDatabase, business_id: str, date: datetime):
    """Obtiene todas las citas de un negocio para un día específico."""
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    return await db["appointments"].find({
        "business_id": ObjectId(business_id),
        "appointment_time": {"$gte": start_of_day, "$lt": end_of_day}
    }).to_list(1000)