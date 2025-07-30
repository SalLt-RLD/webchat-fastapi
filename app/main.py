from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, rooms, messages, websockets

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://localhost:63342",
    "http://localhost:63343"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(messages.router, prefix="/rooms", tags=["Messages"])
app.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])
