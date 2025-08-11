from  fastapi import APIRouter, HTTPException, status, Depends , Security
from app.config import supabase
from app.books.models import BookCreate, BookUpdate
from app.utils.auth_guard import get_current_user, require_role

book_router = APIRouter()

@book_router.post("/", response_model=BookCreate)
def create_book(payload: BookCreate, user=Security(require_role("admin"))):
    """Create a new book."""
    try:
        result = supabase.table("Books").insert(payload.dict()).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book creation failed")
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@book_router.get("/",response_model=list[BookCreate])
def list_books(user=Security(require_role("admin"))):
    """List all books."""
    try:
        result = supabase.table("Books").select("*").execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.patch("/{book_id}", response_model=BookUpdate)
def update_book(book_id: str, payload: BookUpdate, user=Security(require_role("admin"))):
    """Update a book's details."""
    try:
        print("As dict:", payload.dict()) 
        print("As dict (exclude_unset):", payload.dict(exclude_unset=True))
        result = supabase.table("Books").update(payload.dict(exclude_unset=True)).eq("id", book_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.delete("/{book_id}")
def delete_book(book_id: str, user=Security(require_role("admin"))):
    """Delete a book."""
    try:
        result = supabase.table("Books").delete().eq("id", book_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return {"message": "Book deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))