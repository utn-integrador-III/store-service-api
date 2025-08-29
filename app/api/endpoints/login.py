
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import requests

from app.db.session import get_database
from app.crud.crud_user import get_user_by_email, get_or_create_social_user
from app.schemas.user import Token
from app.core.config import settings
from app.core.security import verify_password, create_access_token

router = APIRouter()

class SocialToken(BaseModel):
    token: str

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

@router.post("/google", response_model=Token)
async def login_google(
    social_token: SocialToken,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {social_token.token}"}
        response = requests.get(user_info_url, headers=headers)
        
        if not response.ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Google inválido.")
            
        user_info = response.json()
        user_email = user_info.get("email")
        user_name = user_info.get("name")
        user_picture = user_info.get("picture") 

        if not user_email:
            raise HTTPException(status_code=400, detail="No se pudo obtener el email de Google.")

        user = await get_or_create_social_user(db, {"email": user_email, "name": user_name, "picture": user_picture})
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrió un error en el servidor: {e}")