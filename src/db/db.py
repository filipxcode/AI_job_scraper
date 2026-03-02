from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.models import Base
from ..config.settings import get_settings

engine = None
SessionLocal = None


def _ensure_db_initialized():
    global engine, SessionLocal
    if engine is not None and SessionLocal is not None:
        return

    settings = get_settings()
    engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session_factory():
    _ensure_db_initialized()
    return SessionLocal


def init_db():
    _ensure_db_initialized()
    Base.metadata.create_all(bind=engine)