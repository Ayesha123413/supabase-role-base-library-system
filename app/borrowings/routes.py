from fastapi import APIRouter, HTTPException, status, Depends,Security
from app.config import supabase, supabase_admin
from app.borrowings.models from BorrowBookRequest,BorrowingResponse
from datetime import date,datetime
from app.utils.auth_guard import get_current_user, require_role


borrow_router = APIRouter()