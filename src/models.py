from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500), unique=True)
    source: Mapped[str] = mapped_column(String(50))
    skills: Mapped[str] = mapped_column(Text)
    ai_score: Mapped[int | None] = mapped_column(Integer)
    ai_summary: Mapped[str | None] = mapped_column(String(1000)) 
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return (
            "Offer("
            f"title={self.title!r}, "
            f"company={self.company!r}, "
            f"city={self.city!r}, "
            f"source={self.source!r}, "
            f"url={self.url!r}, "
            f"skills={self.skills!r}"
            f"score={self.ai_score!r}"
            ")"
        )