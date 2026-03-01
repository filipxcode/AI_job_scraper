from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .models import JobOffer
from .schemas import JobOfferCreate

class JobRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def check_if_exists(self, url: str) -> bool:
        with self.session_factory() as db:
            result = db.execute(select(JobOffer).where(JobOffer.url == url))
            return result.scalars().first() is not None

    def save_offer(self, offer_data: JobOfferCreate):
        with self.session_factory() as db:
            new_offer = JobOffer(**offer_data.model_dump())
            db.add(new_offer)
            db.commit()
    
    def get_offers_for_llm(self) -> list[JobOffer]:
        with self.session_factory() as db:
            result = db.execute(select(JobOffer).where(JobOffer.ai_summary.is_(None)))
            return result.scalars().all()
    
    def update_ai(self, offer_id: int, ai_score: int | None, ai_summary: str | None) -> None:
        with self.session_factory() as db:
            stmt = (
                update(JobOffer)
                .where(JobOffer.id == offer_id)
                .values(ai_score=ai_score, ai_summary=ai_summary)
            )
            db.execute(stmt)
            db.commit()