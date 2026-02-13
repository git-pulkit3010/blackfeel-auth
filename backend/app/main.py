from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .database import engine, Base
from .auth import routes as auth_routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend to access
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.94.99:3000",
    "https://overtense-kimberli-protrusile.ngrok-free.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth API"}
