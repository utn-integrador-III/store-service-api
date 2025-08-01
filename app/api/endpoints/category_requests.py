from fastapi import APIRouter, Depends, status, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.user import UserResponse
from app.schemas.category_request import CategoryRequestBase, CategoryRequestResponse
from app.crud.crud_category_request import create_category_request
from .businesses import get_current_owner_user

router = APIRouter()

@router.post("/", response_model=CategoryRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_category_request(
    request_in: CategoryRequestBase,
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    """
    Permite a un dueño enviar una solicitud para una nueva categoría.
    """
    request_data_with_owner = request_in.model_dump()
    request_data_with_owner['owner_id'] = owner.id
    
    request = await create_category_request(db, request_data_with_owner)
    
   
    return CategoryRequestResponse.model_validate(request)