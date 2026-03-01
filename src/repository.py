from .models import JobOffer
from .db import SessionLocal
from .schemas import JobOfferBase
from sqlalchemy import select

class JobRepository:
    def __init__(self, session):
        self.session = session 
    
    def save_offer(self, job_data: JobOfferBase):
        data = JobOffer(**job_data.model_dump())
        self.session.add(data)
        self.session.commit()
    
    def check_if_exists(self, url: str):
        result = self.session.execute(select(JobOffer).where(url == JobOffer.url))
        return result.scalars().first() is not None