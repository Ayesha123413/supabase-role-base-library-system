from fastapi import APIRouter, HTTPException, status, Depends,Security
from app.config import supabase, supabase_admin
from app.borrowings.models from BorrowBookRequest,BorrowingResponse
from datetime import date,datetime
from app.utils.auth_guard import get_current_user, require_role


borrow_router = APIRouter()

@borrow_router.post("/",response_model:BorrowBookRequest)
def borrow_book(payload: BorrowBookRequest,user=Depends(require_role("member"))):
    book=supabase.table("books").select("*").eq("id",payload.book_id).single().execute
    if not book.data:
        raise HTTP_404_NOT_FOUND(status_code:404 , detail="Book not found")
    if book.data.quantity<=0:
        raise HTTPException(status_code:400,detail:"Book not available")
    
    borrowing_data={
       " user_id":user.id,
        "book_id":payload.book_id,
        "borrow_date":data.today().isofromat()
        "due_date":payload.due_date.isoformat()
        "status":"borrowed"
    }
    borrowing=supabase.table("borrowing").insert(borrowing_data).execute()
    supabase.table("books").update({quantity:book.data.quantity-1}).eq("id",payload.book_id).execute()
    return borrowing.data[0]
