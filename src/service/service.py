import logging
from .parser import JobParser
from ..utils.llm import LLMProcessor
from ..db.db import get_session_factory, init_db
from .repository import JobRepository
from .scrapers import NoFluffJobs, JustJoinIt
from ..schemas.schemas import JobOfferBase, JobOfferCreate
from ..config.settings import get_settings
from ..utils.telegram import TelegramNotifier, format_offer_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppService:
    def __init__(self, path: str = "data/candidate_data.txt"):
        """High-level application orchestrator (scrape -> store -> optional LLM scoring)."""
        init_db()
        self.scrapers = [NoFluffJobs(), JustJoinIt()]
        self.parser = JobParser()
        self.llm: LLMProcessor | None = None
        self.repo = JobRepository(get_session_factory())
        self.candidate_data = self._get_candidate_data(path)
        
    def _get_candidate_data(self, path: str) -> str:
        """Load candidate profile text from disk."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Candidate profile file not found: {path}")
            return ""
    
    def scrape(self) -> list[JobOfferCreate]:
        """Fetch raw offers from all scrapers and normalize them into DTOs."""
        all_data: list[dict] = []
        for scraper in self.scrapers:
            data = scraper.fetch_all()
            all_data.extend(data)

        parsed_data = self.parser.parse(all_data)
        logger.info(f"Parsed offers: {len(parsed_data)}")
        return parsed_data

    def scrape_and_store(self) -> int:
        """Scrape offers and persist new ones into the database."""
        offers = self.scrape()
        inserted = self.repo.save_offers(offers)
        logger.info(f"Inserted new offers into DB: {inserted}")
        return inserted
    
    def llm_check(self):
        """Run LLM scoring for offers that have not been summarized yet."""
        settings = get_settings()
        notifier: TelegramNotifier | None = None
        if settings.TELEGRAM_BOT_API_KEY and settings.TELEGRAM_CHAT_ID:
            try:
                notifier = TelegramNotifier()
            except Exception as e:
                logger.warning(f"Telegram notifications disabled: {e}")

        if self.llm is None:
            self.llm = LLMProcessor()

        offers = self.repo.get_offers_for_llm()
        for offer in offers[:50]:
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

            if notifier and ai_response.score >= settings.min_ai_score:
                try:
                    notifier.send_message(
                        format_offer_message(
                            title=offer_pydantic.title,
                            company=offer_pydantic.company,
                            score=ai_response.score,
                            summary=ai_response.summary,
                            url=offer_pydantic.url,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Telegram message: {e}")

    def run(self, mode: str = "all") -> None:
        """Run the selected flow: scrape, llm, or all."""
        mode = (mode or "all").lower()
        if mode not in {"scrape", "llm", "all"}:
            raise ValueError("mode must be one of: scrape, llm, all")

        if mode in {"scrape", "all"}:
            self.scrape_and_store()

        if mode in {"llm", "all"}:
            self.llm_check()
            
