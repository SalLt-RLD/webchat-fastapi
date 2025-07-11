from fastapi import FastAPI
from app.api import auth, rooms, messages

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(messages.router, prefix="/rooms", tags=["Messages"])
