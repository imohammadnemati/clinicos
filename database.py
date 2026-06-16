"""
ClinicOS – Database Management
SQLAlchemy setup, session management, and database initialization.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool, QueuePool
from config import DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, DATABASE_POOL_TIMEOUT, DATABASE_POOL_RECYCLE, DEBUG_MODE
from models import Base
from datetime import datetime  # <-- اضافه شد
import logging

logger = logging.getLogger(__name__)


def create_db_engine():
    """
    Create database engine with appropriate settings for SQLite or PostgreSQL.
    """
    is_sqlite = DATABASE_URL.startswith("sqlite")

    if is_sqlite:
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True
        )
        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        logger.info("SQLite engine created with foreign_keys=ON")
    else:
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            poolclass=QueuePool,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_MAX_OVERFLOW,
            pool_timeout=DATABASE_POOL_TIMEOUT,
            pool_recycle=DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,
            pool_use_lifo=True
        )
        logger.info(
            f"PostgreSQL engine created with pool_size={DATABASE_POOL_SIZE}, "
            f"max_overflow={DATABASE_MAX_OVERFLOW}"
        )

    return engine


# Create engine and session factory
engine = create_db_engine()
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )
)


def init_db():
    """Create all tables and default clinic/staff if not exists."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully.")
    create_default_clinic()


def create_default_clinic():
    """Create a default clinic and owner if none exist (single‑clinic mode)."""
    from models import Clinic, Staff
    from config import OWNER_TELEGRAM_ID

    db = SessionLocal()
    try:
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(name="Default Clinic", subdomain="default")
            db.add(clinic)
            db.commit()
            logger.info(f"Default clinic created with ID {clinic.id}.")

        if OWNER_TELEGRAM_ID:
            owner = db.query(Staff).filter_by(telegram_id=OWNER_TELEGRAM_ID).first()
            if not owner:
                owner = Staff(
                    clinic_id=clinic.id,
                    telegram_id=OWNER_TELEGRAM_ID,
                    name="Clinic Owner",
                    role="owner",
                    created_at=datetime.utcnow()
                )
                db.add(owner)
                db.commit()
                logger.info(f"Owner staff created for telegram_id {OWNER_TELEGRAM_ID}.")
    except Exception as e:
        logger.error(f"Error creating default clinic: {e}")
        db.rollback()
    finally:
        db.close()


def get_db():
    """Yield a database session (for dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Return a direct session (caller must close)."""
    return SessionLocal()


def close_all_sessions():
    """Dispose of the engine and remove scoped session."""
    SessionLocal.remove()
    engine.dispose()
    logger.info("All database connections closed.")


def database_health_check() -> dict:
    """Check database connectivity and return status."""
    result = {
        "status": "unknown",
        "latency_ms": None,
        "error": None
    }
    try:
        import time
        start = time.time()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        latency = (time.time() - start) * 1000
        result["status"] = "healthy"
        result["latency_ms"] = round(latency, 2)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        result["status"] = "unhealthy"
        result["error"] = str(e)
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("Database Manager – ClinicOS")
    print("=" * 50)
    init_db()
    health = database_health_check()
    print(f"Health: {health}")