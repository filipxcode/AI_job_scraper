import logging
from .parser import JobParser
from .llm import LLMProcessor
from .db import SessionLocal
from .repository import JobRepository
from .scrapers import NoFluffJobs, JustJoinIt
from .models import JobOffer
from .schemas import JobOfferBase
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppService:
    def __init__(self, path: str = "data/candidate_data.txt"):
        self.scrapers = [NoFluffJobs(), JustJoinIt()]
        self.parser = JobParser()
        self.llm = LLMProcessor()
        self.repo = JobRepository(SessionLocal)
        self.candidate_data = self._get_candidate_data(path)
        
    def _get_candidate_data(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Nie znaleziono pliku z danymi kandydata: {path}")
            return ""
    
    def _process_data(self):
        all_data = []
        for scraper in self.scrapers:
            data = scraper.fetch_all()
            if scraper.__class__.__name__ == "JustJoinIt":
                logger.info(f"Dane ze scrapera {scraper.__class__.__name__}: {data}")
            all_data.extend(data)

        parsed_data = self.parser.parse(all_data)
        logger.info(f"Sparsowane dane: {parsed_data}")
        for item in parsed_data:
            print(item) 
            
    def save_to_db(self, data: list[JobOffer]):
        for d in data:
            if not self.repo.check_if_exists(d):
                self.repo.save_offer(d)
    
    def llm_check(self):
        offers = self.repo.get_offers_for_llm()
        for offer in offers:
            offer_pydantic = JobOfferBase.model_validate(offer)
            ai_response = self.llm.process_query(candidate_data=self.candidate_data, job_data=offer_pydantic.model_dump())
            if ai_response is None:
                logger.error(f"Offer {offer} with no AI response")
                continue
            self.repo.update_ai(
                offer_id=offer.id,
                ai_score=ai_response.score,
                ai_summary=ai_response.summary,
            )
            