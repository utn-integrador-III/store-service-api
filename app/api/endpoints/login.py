
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_database
from app.crud.crud_user import get_user_by_email
from app.schemas.user import Token
from app.core.config import settings
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    db: AsyncIOMotorDatabase = Depends(get_database),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await get_user_by_email(db, email=form_data.username)
    
   
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}