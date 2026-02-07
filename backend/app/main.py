from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import whatsapp_webhooks

load_dotenv()

from .database import engine, Base
from .auth import routes as auth_routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend to access
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(whatsapp_webhooks.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth API"}
