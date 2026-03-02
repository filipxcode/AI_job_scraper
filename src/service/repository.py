from sqlalchemy import select, update
from ..models.models import JobOffer
from ..schemas.schemas import JobOfferCreate

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

    def save_offers(self, offers: list[JobOfferCreate]) -> int:
        if not offers:
            return 0

        urls = [o.url for o in offers if o.url]
        if not urls:
            return 0

        with self.session_factory() as db:
            existing_urls = set(
                db.execute(select(JobOffer.url).where(JobOffer.url.in_(urls))).scalars().all()
            )

            inserted = 0
            for offer in offers:
                if not offer.url or offer.url in existing_urls:
                    continue
                db.add(JobOffer(**offer.model_dump()))
                inserted += 1

            if inserted:
                db.commit()
            return inserted
    
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