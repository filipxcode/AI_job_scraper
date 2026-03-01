from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .settings import get_settings

settings = get_settings()
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)