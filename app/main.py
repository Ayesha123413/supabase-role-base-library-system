from fastapi import FastAPI
from app.auth.routes import auth_router
from app.users.routes import user_router
# from app.books.routes import book_router
# from app.borrowings.routes import borrow_router


app=FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
# app.include_router(book_router, prefix="/books")
# app.include_router(borrow_router, prefix="/borrowings")
