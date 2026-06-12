"""
مدیریت دیتابیس (Database Manager)
نسخه پایدار با پشتیبانی از SQLite و PostgreSQL،
شامل connection pooling, health check, scoped_session
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool, QueuePool
from config import (
    DATABASE_URL,
    DATABASE_POOL_SIZE,
    DATABASE_MAX_OVERFLOW,
    DATABASE_POOL_TIMEOUT,
    DATABASE_POOL_RECYCLE,
    DEBUG_MODE
)
from models import Base
import logging
import time

logger = logging.getLogger(__name__)


def create_db_engine():
    """
    ایجاد موتور دیتابیس با تنظیمات مناسب برای SQLite یا PostgreSQL
    """
    is_sqlite = DATABASE_URL.startswith("sqlite")

    if is_sqlite:
        # تنظیمات SQLite (بدون pooling پیشرفته)
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            connect_args={"check_same_thread": False},  # برای محیط چندنخی
            poolclass=StaticPool,                       # مناسب برای SQLite
            pool_pre_ping=True                          # بررسی سلامت اتصال
        )
        # فعال‌سازی کلیدهای خارجی در SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        logger.info("SQLite engine created with foreign_keys=ON")
    else:
        # تنظیمات PostgreSQL (با connection pooling)
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            poolclass=QueuePool,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_MAX_OVERFLOW,
            pool_timeout=DATABASE_POOL_TIMEOUT,
            pool_recycle=DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,      # بررسی سلامت اتصال قبل از استفاده
            pool_use_lifo=True       # استفاده از آخرین اتصال برای کاهش fragmentation
        )
        logger.info(
            f"PostgreSQL engine created with pool_size={DATABASE_POOL_SIZE}, "
            f"max_overflow={DATABASE_MAX_OVERFLOW}"
        )

    return engine


# ایجاد موتور دیتابیس
engine = create_db_engine()

# ایجاد session factory با scoped_session برای جلوگیری از تداخل
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False   # جلوگیری از خطاهای عجیب بعد از commit
    )
)


def init_db():
    """ایجاد جداول دیتابیس (بر اساس مدل‌ها)"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ جداول دیتابیس با موفقیت ایجاد شدند.")
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول: {e}")
        raise


def get_db():
    """
    دریافت سشن دیتابیس (برای استفاده در Dependency Injection)
    استفاده:
        with get_db() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    دریافت سشن دیتابیس (استفاده مستقیم – بستن دستی)
    """
    return SessionLocal()


def database_health_check() -> dict:
    """
    بررسی سلامت دیتابیس (برای مانیتورینگ)
    بازگشت: دیکشنری شامل وضعیت اتصال و تأخیر
    """
    result = {
        "status": "unknown",
        "latency_ms": None,
        "pool_size": None,
        "pool_checkedin": None,
        "pool_overflow": None,
        "error": None
    }
    try:
        start = time.time()
        # اجرای یک کوئری ساده برای تست اتصال
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        latency = (time.time() - start) * 1000
        result["status"] = "healthy"
        result["latency_ms"] = round(latency, 2)

        # اطلاعات pool (فقط برای PostgreSQL)
        if hasattr(engine.pool, "size"):
            result["pool_size"] = engine.pool.size()
            result["pool_checkedin"] = engine.pool.checkedin()
            result["pool_overflow"] = engine.pool.overflow()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        result["status"] = "unhealthy"
        result["error"] = str(e)

    return result


def close_all_sessions():
    """بستن تمام سشن‌های فعال (در زمان خروج برنامه)"""
    SessionLocal.remove()
    engine.dispose()
    logger.info("✅ تمام اتصالات دیتابیس بسته شدند.")


def backup_database(backup_path: str = None) -> bool:
    """
    پشتیبان‌گیری از دیتابیس (فقط برای SQLite)
    """
    import shutil
    from datetime import datetime

    if not DATABASE_URL.startswith("sqlite"):
        logger.warning("پشتیبان‌گیری فقط برای SQLite پشتیبانی می‌شود.")
        return False

    try:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        logger.info(f"پشتیبان دیتابیس در {backup_path} ذخیره شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در پشتیبان‌گیری: {e}")
        return False


def get_database_size() -> int:
    """دریافت حجم دیتابیس (بایت) – فقط SQLite"""
    if not DATABASE_URL.startswith("sqlite"):
        return 0
    import os
    db_path = DATABASE_URL.replace("sqlite:///", "")
    try:
        return os.path.getsize(db_path)
    except:
        return 0


# اگر فایل به صورت مستقیم اجرا شد
if __name__ == "__main__":
    print("=" * 50)
    print("Database Manager - ClinicOS")
    print("=" * 50)
    init_db()
    health = database_health_check()
    print(f"Database health: {health}")
    print(f"Database size: {get_database_size() / 1024:.2f} KB")