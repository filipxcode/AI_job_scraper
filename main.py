
import logging
from src.service import AppService

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("main")
    logger.info("Start aplikacji AI Job Scraper")
    app = AppService()
    logger.info("Rozpoczynam przetwarzanie danych...")
    app._process_data()
    logger.info("Zakończono przetwarzanie danych.")