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

# 2. Return a book (member or librarian)
@borrow_router.post("/{borrowing_id}/return", response_model=BorrowingResponse)
def return_book(borrowing_id: str, user=Depends(get_current_user)):
    # Get borrowing record
    borrowing = supabase.table("Borrowings").select("*").eq("id", borrowing_id).single().execute()
    print("borrowing data =", borrowing.data)
    if not borrowing.data:
        raise HTTPException(status_code=404, detail="Borrowing record not found")

    # Ensure only borrower OR librarian/admin can return
    if borrowing.data["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to return this book")

    if borrowing.data["status"] == "returned":
        raise HTTPException(status_code=400, detail="Book already returned")

    # Update borrowing record
    updated = supabase.table("Borrowings").update({
        "status": "returned",
        "return_date": date.today().isoformat()
    }).eq("id", borrowing_id).execute()

    # Increment book quantity
    book = supabase.table("Books").select("*").eq("id", borrowing.data["book_id"]).single().execute()
    print("book data =",book.data["quantity"])
    supabase.table("Books").update({"quantity": book.data["quantity"] + 1}).eq("id", book.data["id"]).execute()
    return updated.data[0]


# 3. Get borrowings (member = own only, librarian/admin = all)
@borrow_router.get("/", response_model=list[BorrowingResponse])
def list_borrowings(user=Depends(get_current_user)):
    query = supabase.table("Borrowings").select("*")

    if user.role == "member":
        print("User role is member")
        query = query.eq("user_id", user.id)
        print("Member user - fetching own borrowings",user.id)

    records = query.execute()
    return records.data


@borrow_router.get("/overdue", response_model=list[BorrowingResponse])
def overdue_books(user=Depends(require_role("librarian"))):
    today = date.today().isoformat()
    records = supabase.table("Borrowings").select("*").eq("status", "borrowed").lt("due_date", today).execute()
    return records.data