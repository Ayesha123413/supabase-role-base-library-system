from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.config import supabase

auth_router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@auth_router.post("/register")
def register_user(payload: RegisterRequest):
    result = supabase.auth.sign_up(
       { "email":payload.email,
        "password":payload.password,
        }
    )
    if result.error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error.message
        )
    user = result.user
    supabase.table("Profiles").insert({
        "id": user["id"],
        "email":payload.email,
        "password": payload.password,
        "full_name":payload.full_name,
        "role":ayload.role
    }).execute()
    return {"message": "User registered successfully", "user_id": user["id"]}

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