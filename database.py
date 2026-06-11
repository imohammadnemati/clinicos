from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL
from models import Base
import logging

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("دیتابیس راه‌اندازی شد.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()