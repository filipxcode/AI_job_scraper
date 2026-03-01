import logging
from .parser import JobParser
from .llm import LLMProcessor
from .db import SessionLocal
from .repository import JobRepository
from .scrapers import NoFluffJobs, JustJoinIt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppService:
    def __init__(self):
        self.scrapers = [NoFluffJobs(), JustJoinIt()]
        self.parser = JobParser()
        self.llm = LLMProcessor()
        self.repo = JobRepository(SessionLocal)
        
    def _process_data(self):
        all_data = []
        for scraper in self.scrapers:
            data = scraper.fetch_all()
            logger.info(f"Dane ze scrapera {scraper.__class__.__name__}: {data}")
            all_data.extend(data)

        parsed_data = self.parser.parse(all_data)
        logger.info(f"Sparsowane dane: {parsed_data}")
        for item in parsed_data:
            print(item) 
