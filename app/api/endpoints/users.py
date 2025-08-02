from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_database
from app.crud import crud_user
from app.schemas.category import CategoryRequestSchema
from app.schemas.user import UserCreate, UserResponse, UserUpdate, OwnerRequestSchema
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    existing_user = await crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con este correo electrónico.",
        )
    user = await crud_user.create_user(db, user=user_in)
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(user_in: UserUpdate, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    user_id = str(current_user.id)
    updated_user = await crud_user.update_user(db, user_id=user_id, user_in=user_in)
    return updated_user

@router.post("/me/request-owner", response_model=UserResponse)
async def request_owner_role(
    request_data: OwnerRequestSchema,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    user_id = str(current_user.id)
    updated_user = await crud_user.create_owner_request(db, user_id=user_id, request_data=request_data)
    return updated_user


@router.get("/admin/owner-requests", response_model=List[UserResponse])
async def get_pending_owner_requests(db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_admin_user)):
    pending_users = await crud_user.get_pending_owner_requests(db)
    return pending_users

@router.post("/admin/approve-owner/{user_id}", response_model=UserResponse)
async def approve_owner(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_admin_user)):
    approved_user = await crud_user.approve_owner_request(db, user_id)
    if not approved_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o la solicitud no pudo ser aprobada")
    return approved_user

@router.post("/admin/reject-owner/{user_id}", response_model=UserResponse)
async def reject_owner(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    user_to_reject = await crud_user.get_user_by_id(db, user_id)
    if not user_to_reject:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    rejected_user = await crud_user.reject_owner_request(db, user_id)
    return rejected_user

@router.get("/admin/owners", response_model=List[UserResponse])
async def get_all_owners(db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_admin_user)):
    owners = await crud_user.get_all_owners(db)
    return owners

@router.get("/admin/category-requests", response_model=List[CategoryRequestSchema])
async def get_pending_category_requests_route(db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_admin_user)):
    requests = await crud_user.get_pending_category_requests(db)
    return requests