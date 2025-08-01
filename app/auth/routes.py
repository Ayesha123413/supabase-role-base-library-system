from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.config import supabase
from uuid import UUID
from typing import Optional  

auth_router = APIRouter()


class RegisterRequest(BaseModel):
    id: Optional[UUID] = None
    email: EmailStr
    password: str
    full_name: str
    role: str
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@auth_router.post("/register")
def register_user(payload: RegisterRequest):
    try:

         result = supabase.auth.sign_up(
             { "email":payload.email,
              "password":payload.password,
              }
              )
    except Exception as e:
        if "user already exists" in str(e):
            raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="User already exists"
                  )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) 
            )
    user = result.user
    if not user:
        raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="User registration failed"
             )
    supabase.from_("Profiles").insert({
        "id": user.id,
        "email": payload.email,
        "full_name": payload.full_name,
        "role": payload.role
        }).execute()
    return {"message": "User registered successfully", "user": user.id}


@auth_router.post("/login")
def login_user(payload: LoginRequest):
    result = supabase.auth.sign_in_with_password({
        "email":payload.email,
        "password":payload.password
        })
    if result.error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error.message
        )
    return {
        "token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user": result.user,
        }