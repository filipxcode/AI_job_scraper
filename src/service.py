import logging
from .parser import JobParser
from .llm import LLMProcessor
from .db import SessionLocal, init_db
from .repository import JobRepository
from .scrapers import NoFluffJobs, JustJoinIt
from .schemas import JobOfferBase, JobOfferCreate
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppService:
    def __init__(self, path: str = "data/candidate_data.txt"):
        init_db()
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
    
    def scrape(self) -> list[JobOfferCreate]:
        all_data: list[dict] = []
        for scraper in self.scrapers:
            data = scraper.fetch_all()
            all_data.extend(data)

        parsed_data = self.parser.parse(all_data)
        logger.info(f"Sparsowano ofert: {len(parsed_data)}")
        return parsed_data

    def scrape_and_store(self) -> int:
        offers = self.scrape()
        inserted = self.repo.save_offers(offers)
        logger.info(f"Zapisano nowych ofert do DB: {inserted}")
        return inserted
    
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

    def run(self, mode: str = "all") -> None:
        mode = (mode or "all").lower()
        if mode not in {"scrape", "llm", "all"}:
            raise ValueError("mode must be one of: scrape, llm, all")

        if mode in {"scrape", "all"}:
            self.scrape_and_store()

        if mode in {"llm", "all"}:
            self.llm_check()
            