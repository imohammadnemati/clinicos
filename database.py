"""
فایل مدیریت دیتابیس (Database Management)
این فایل مسئول راه‌اندازی و مدیریت اتصالات دیتابیس است.
شامل:
- ایجاد موتور دیتابیس (SQLite/PostgreSQL)
- مدیریت سشن‌ها
- توابع کمکی برای عملیات پایه دیتابیس
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from config import DATABASE_URL, DEBUG_MODE
from models import Base
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)


# ========== ایجاد موتور دیتابیس ==========
def create_db_engine():
    """
    ایجاد موتور دیتابیس بر اساس DATABASE_URL
    پشتیبانی از SQLite و PostgreSQL
    """
    if DATABASE_URL.startswith("sqlite"):
        # تنظیمات ویژه SQLite
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            connect_args={"check_same_thread": False},  # برای SQLite در محیط چندنخی
            poolclass=StaticPool,  # برای SQLite
            pool_pre_ping=True
        )
        
        # فعال‌سازی کلیدهای خارجی در SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
        logger.info("✅ دیتابیس SQLite راه‌اندازی شد.")
    else:
        # تنظیمات PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        logger.info("✅ دیتابیس PostgreSQL راه‌اندازی شد.")
    
    return engine


# ایجاد موتور دیتابیس
engine = create_db_engine()

# ایجاد سشن فکتوری
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))


# ========== توابع مدیریت دیتابیس ==========
def init_db():
    """
    راه‌اندازی اولیه دیتابیس
    ایجاد تمام جداول تعریف شده در مدل‌ها
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ تمام جداول دیتابیس با موفقیت ایجاد شدند.")
        
        # ایجاد کلینیک پیش‌فرض (در صورت نبود)
        create_default_clinic()
        
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول دیتابیس: {e}")
        raise


def create_default_clinic():
    """
    ایجاد کلینیک پیش‌فرض در صورتی که هیچ کلینیکی وجود نداشته باشد
    """
    from models import Clinic, Staff
    from config import OWNER_TELEGRAM_ID, BOT_TOKEN
    
    db = SessionLocal()
    try:
        # بررسی وجود کلینیک
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(
                name="کلینیک پیش‌فرض",
                subdomain="default",
                created_at=datetime.utcnow()
            )
            db.add(clinic)
            db.commit()
            logger.info(f"✅ کلینیک پیش‌فرض با شناسه {clinic.id} ایجاد شد.")
        
        # بررسی وجود مالک
        if OWNER_TELEGRAM_ID:
            owner = db.query(Staff).filter_by(telegram_id=OWNER_TELEGRAM_ID).first()
            if not owner:
                owner = Staff(
                    clinic_id=clinic.id,
                    telegram_id=OWNER_TELEGRAM_ID,
                    name="مالک کلینیک",
                    role="owner",
                    created_at=datetime.utcnow()
                )
                db.add(owner)
                db.commit()
                logger.info(f"✅ کاربر مالک با شناسه {OWNER_TELEGRAM_ID} ایجاد شد.")
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد کلینیک پیش‌فرض: {e}")
        db.rollback()
    finally:
        db.close()


def get_db():
    """
    دریافت یک سشن دیتابیس (برای استفاده در درخواست‌ها)
    استفاده به عنوان context manager:
    
    with get_db() as db:
        db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    دریافت یک سشن دیتابیس (استفاده مستقیم)
    توجه: کاربر مسئول بستن سشن است
    """
    return SessionLocal()


def close_db_session():
    """
    بستن تمام سشن‌های فعال
    """
    SessionLocal.remove()
    logger.info("🔒 تمام سشن‌های دیتابیس بسته شدند.")


# ========== توابع کمکی برای عملیات رایج ==========
def execute_raw_query(query: str, params: dict = None):
    """
    اجرای یک کوئری خام (فقط برای مواقع ضروری)
    """
    db = SessionLocal()
    try:
        result = db.execute(query, params or {})
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"خطا در اجرای کوئری خام: {e}")
        raise
    finally:
        db.close()


def table_exists(table_name: str) -> bool:
    """
    بررسی وجود یک جدول در دیتابیس
    """
    db = SessionLocal()
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        exists = inspector.has_table(table_name)
        return exists
    finally:
        db.close()


def get_table_names() -> list:
    """
    دریافت لیست تمام جداول دیتابیس
    """
    db = SessionLocal()
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.get_table_names()
    finally:
        db.close()


def backup_database(backup_path: str = None):
    """
    پشتیبان‌گیری از دیتابیس (فقط برای SQLite)
    """
    import shutil
    from datetime import datetime
    
    if not DATABASE_URL.startswith("sqlite"):
        logger.warning("پشتیبان‌گیری فقط برای SQLite پشتیبانی می‌شود.")
        return False
    
    try:
        # استخراج مسیر فایل SQLite
        db_path = DATABASE_URL.replace("sqlite:///", "")
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        
        shutil.copy2(db_path, backup_path)
        logger.info(f"✅ پشتیبان از دیتابیس در {backup_path} ذخیره شد.")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در پشتیبان‌گیری: {e}")
        return False


def get_database_size() -> int:
    """
    دریافت حجم دیتابیس (بر حسب بایت)
    """
    if not DATABASE_URL.startswith("sqlite"):
        return 0
    
    import os
    db_path = DATABASE_URL.replace("sqlite:///", "")
    try:
        return os.path.getsize(db_path)
    except:
        return 0


def vacuum_database():
    """
    بهینه‌سازی دیتابیس (فقط برای SQLite)
    """
    if not DATABASE_URL.startswith("sqlite"):
        logger.warning("بهینه‌سازی فقط برای SQLite پشتیبانی می‌شود.")
        return False
    
    try:
        db = SessionLocal()
        db.execute("VACUUM")
        db.commit()
        db.close()
        logger.info("✅ دیتابیس بهینه‌سازی شد.")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در بهینه‌سازی دیتابیس: {e}")
        return False


# ========== کلاس Context Manager برای مدیریت سشن ==========
class DBSession:
    """
    Context manager برای مدیریت خودکار سشن دیتابیس
    استفاده:
    
    with DBSession() as db:
        db.query(User).all()
    """
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()


# ========== ایمپورت datetime برای استفاده در توابع ==========
from datetime import datetime


# اگر فایل به صورت مستقیم اجرا شد
if __name__ == "__main__":
    print("=" * 50)
    print("مدیریت دیتابیس ClinicOS")
    print("=" * 50)
    
    # راه‌اندازی دیتابیس
    init_db()
    
    # نمایش اطلاعات
    print(f"\n📊 اطلاعات دیتابیس:")
    print(f"   نوع: {'SQLite' if DATABASE_URL.startswith('sqlite') else 'PostgreSQL'}")
    print(f"   آدرس: {DATABASE_URL}")
    print(f"   حجم: {get_database_size() / 1024:.2f} KB")
    
    tables = get_table_names()
    print(f"   تعداد جداول: {len(tables)}")
    
    if tables:
        print("\n📋 لیست جداول:")
        for table in tables[:20]:  # حداکثر 20 جدول
            print(f"   - {table}")
        if len(tables) > 20:
            print(f"   ... و {len(tables) - 20} جدول دیگر")
    
    print("\n✅ دیتابیس آماده است.")