from fastapi import FastAPI
from app.routers import auth as auth_router, todo as todo_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(todo_router.router)
