
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.business import BusinessCreate, BusinessUpdate, Schedule

async def get_business(db: AsyncIOMotorDatabase, business_id: str):
    """
    Busca un único negocio en la base de datos por su ID.
    """
    if not ObjectId.is_valid(business_id):
        return None
    return await db.businesses.find_one({"_id": ObjectId(business_id)})

async def get_published_businesses(db: AsyncIOMotorDatabase):
    """
    Obtiene todos los negocios que tienen el estado 'published'.
    """
    cursor = db.businesses.find({"status": "published"})
    return await cursor.to_list(length=None)


async def create_business(db: AsyncIOMotorDatabase, business_in: BusinessCreate, owner_id: str):
    """
    Crea un nuevo negocio en la base de datos.
    """
    business_data = business_in.model_dump()
    

    logo_url = business_data.get("logo_url")
    
    initial_photos = [logo_url] if logo_url else []
    
    business_data.update({
        "owner_id": ObjectId(owner_id),
        "status": "draft",
        "photos": initial_photos, 
        "categories": [],
        "schedule": Schedule().model_dump(), 
        "created_at": datetime.utcnow()
    })
    
    result = await db.businesses.insert_one(business_data)
    new_business = await db.businesses.find_one({"_id": result.inserted_id})
    return new_business


async def update_business(db: AsyncIOMotorDatabase, business_id: str, business_in: BusinessUpdate):
    """
    Actualiza la información de un negocio.
    """
    update_data = business_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_business(db, business_id)
        
    await db.businesses.update_one(
        {"_id": ObjectId(business_id)},
        {"$set": update_data}
    )
    return await get_business(db, business_id)

async def get_businesses_by_owner(db: AsyncIOMotorDatabase, owner_id: str):
    """
    Obtiene todos los negocios que pertenecen a un dueño específico.
    """
    cursor = db.businesses.find({"owner_id": ObjectId(owner_id)})
    return await cursor.to_list(length=None)

async def update_business_status(db: AsyncIOMotorDatabase, business_id: str, status: str):
    """
    Actualiza el estado de un negocio (ej. 'draft' a 'published').
    """
    await db.businesses.update_one(
        {"_id": ObjectId(business_id)},
        {"$set": {"status": status}}
    )
    return await get_business(db, business_id)

async def update_business_schedule(db: AsyncIOMotorDatabase, business_id: str, schedule_in: Schedule):
    """
    Actualiza el horario de un negocio.
    """
    await db.businesses.update_one(
        {"_id": ObjectId(business_id)},
        {"$set": {"schedule": schedule_in.model_dump()}}
    )
    return await get_business(db, business_id)

async def get_available_slots_for_day(db: AsyncIOMotorDatabase, business_id: str, date: str):
    """
    Calcula los horarios disponibles para un negocio en una fecha específica.
    (Esta es una implementación de ejemplo)
    """
    business = await get_business(db, business_id)
    if not business or not business.get("schedule"):
        raise ValueError("El negocio no tiene un horario configurado.")
    
    from datetime import datetime, time, timedelta
    
    try:
        request_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = request_date.strftime("%A").lower()
    except ValueError:
        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")

    day_schedule = business["schedule"].get(day_of_week)
    if not day_schedule or not day_schedule.get("is_active"):
        return []


    open_time = datetime.strptime(day_schedule["open_time"], "%H:%M").time()
    close_time = datetime.strptime(day_schedule["close_time"], "%H:%M").time()
    slot_duration = day_schedule["slot_duration_minutes"]
    
    available_slots = []
    current_time = datetime.combine(request_date, open_time)
    end_time = datetime.combine(request_date, close_time)

    while current_time < end_time:
        available_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=slot_duration)
        
    return available_slots