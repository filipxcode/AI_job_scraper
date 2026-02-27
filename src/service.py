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
        all_parsed = []
        for scraper in self.scrapers:
            data = scraper.fetch_all()
            class_name = scraper.__class__.__name__
            logger.info(f"Dane ze scrapera {class_name}: {data}")
            # Ustal źródło na podstawie klasy scrapera
            if class_name.lower().startswith("justjoin"):
                source = "justjoin"
            elif class_name.lower().startswith("nofluff"):
                source = "nofluff"
            else:
                source = class_name.lower()
            parsed = self.parser.parse(data, source)
            logger.info(f"Sparsowane dane ({source}): {parsed}")
            print(f"Sparsowane dane ({source}):")
            for item in parsed:
                print(item)
            all_parsed.extend(parsed)

if __name__ == '__main__':
    app = AppService()
    app._process_data()