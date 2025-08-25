from fastapi import APIRouter, HTTPException, status, Depends,Security
from app.config import supabase, supabase_admin
from app.borrowings.models import BorrowBookRequest,BorrowingResponse
from datetime import date,datetime,timedelta
from app.utils.auth_guard import get_current_user, require_role


borrow_router = APIRouter()

@borrow_router.post("/",response_model=BorrowBookRequest)
def borrow_book(payload: BorrowBookRequest,user=Depends(require_role("member"))):
    book=supabase.table("Books").select("*").eq("id",payload.book_id).single().execute()
    print("book data =",book.data)
    if not book.data:
        raise HTTP_404_NOT_FOUND(status_code=status.HTTP_404_NOT_FOUND , detail="Book not found")
    book=book.data
    if book["quantity"] <=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Book not available")
    borrow_date = date.today()
    borrowing_data={
        "user_id":user["id"] if isinstance(user, dict) else user.id,
        "book_id":payload.book_id,
        "borrow_date":borrow_date.isoformat(),
        "due_date":(borrow_date + timedelta(days=7)).isoformat(),
        "status":"borrowed"
    }
    borrowing=supabase.table("Borrowings").insert(borrowing_data).execute()
    supabase.table("Books").update({"quantity": book["quantity"] - 1}).eq("id",payload.book_id).execute()
    return borrowing.data[0]
