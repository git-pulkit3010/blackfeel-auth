from app.database import engine, Base
from app.auth import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Tables dropped.")
    
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully with new schema.")

if __name__ == "__main__":
    reset_database()
