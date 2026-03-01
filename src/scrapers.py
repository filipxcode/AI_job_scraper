import requests 
import json
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_fixed
import logging 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_safe(self, url, *args, **kwargs):
        self.logger.info(f"Rozpoczynam pobieranie: {url}")
        try:
            return self.get_data(url, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania {url}: {e}")
            raise
        
    @abstractmethod
    def get_data(self, url, *args, **kwargs):
        pass

class JustJoinIt(BaseScraper):
    BASE_URL = "https://justjoin.it/api/candidate-api/"
    OFFER_FRONTEND_URL = "https://justjoin.it/offers/"

    def __init__(self):
        super().__init__()
        self.categories = ["ai", "python", "data"]
        self.limit = 50
        self.urls = [
            f"{self.BASE_URL}offers?categories={cat}&experienceLevels=junior&itemsCount={self.limit}&from=0"
            for cat in self.categories
        ]
    
    def get_data(self, url) -> list[dict]:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])

    def fetch_all(self):
        all_results = []
        for url in self.urls:
            try:
                offers = self.fetch_safe(url)
                # Dodajemy pełny link do każdej oferty
                for offer in offers:
                    offer['full_url'] = f"{self.OFFER_FRONTEND_URL}{offer.get('slug')}"
                all_results.extend(offers) 
            except Exception:
                continue
        return all_results

class NoFluffJobs(BaseScraper):
    API_URL = "https://nofluffjobs.com/api/search/posting?sort=newest&pageSize=20&salaryCurrency=PLN&salaryPeriod=month&region=pl"
    OFFER_FRONTEND_URL = "https://nofluffjobs.com/job/"

    def __init__(self):
        super().__init__()
        self.payload = {
            "rawSearch": "junior python",
            "common": {
                "category": ["artificial-intelligence"],
                "developerStatus": ["junior"]
            }
        }

    def get_data(self, url, payload=None) -> list[dict]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json().get('postings', [])

    def fetch_all(self):
        try:
            offers = self.fetch_safe(self.API_URL, payload=self.payload)
            for offer in offers:
                slug = offer.get('url')
                offer['full_url'] = f"{self.OFFER_FRONTEND_URL}{slug}"
            return offers
        except Exception:
            self.logger.error(f"Nie udało się pobrać danych z NoFluffJobs.")
            return []