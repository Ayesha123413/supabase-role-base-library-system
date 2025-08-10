from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class BookCreate(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    published_year: Optional[int] = None
    quantity: int=1

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    quantity: Optional[int] = None