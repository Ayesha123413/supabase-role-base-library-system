from pydantic import BaseModel
from typing import Optional
from datetime import date

class BorrowBookRequest(BaseModel):
    book_id: str  # UUID of book
    due_date: date  # When the book should be returned

class BorrowingResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str  # "borrowed" or "returned"
