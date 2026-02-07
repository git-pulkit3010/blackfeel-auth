from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use the URL from the frontend .env.local example provided by the user
# In a real app, this should be in backend/.env
SQLALCHEMY_DATABASE_URL = "postgresql://blackfeel_auth_admin:pulkit3010@localhost/signin_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
