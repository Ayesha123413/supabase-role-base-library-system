from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserProfile(BaseModel):
    id: Optional[str] = None  # UUID can be used if needed
    email: EmailStr
    full_name: str
    role: Literal[ 'admin','librarian', 'member']  # Example roles
  

class UpdateUserRole(BaseModel):
    role: Literal['librarian', 'member']  # Example roles

class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: Literal['librarian', 'member']
    password: str   # Only used at creation, never stored in Profiles

