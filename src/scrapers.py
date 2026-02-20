import requests 
import json
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_fixed
import logging 


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': 'application/json'
}
class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_safe(self, url):
        self.logger.info(f"Rozpoczynam pobieranie: {url}") 
        try:
            return self.get_data(url)
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania {url}: {e}") 
            raise 
        
    @abstractmethod
    def get_data(self):
        pass

class JustJoinIt(BaseScraper):
    BASE_URL = "https://justjoin.it/api/candidate-api/"
    def __init__(self):
        super().__init__()
        self.keywords={"experience":"junior", "categories":["ai","python", "data"]}
        self.limit = 50
        self.urls = []
        self._build_urls()
    
    def _build_urls(self):
        for cat in self.keywords["categories"]:
            self.urls.append(f"{self.BASE_URL}/offers?categories={cat}&experienceLevels={self.keywords["experience"]}&itemsCount={self.limit}&from=0")
    
    def get_data(self, url) -> list[dict]:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        json_res = response.json()
        return json_res.get('data', [])

    def fetch_all(self):
        all_results = []
        for url in self.urls:
            try:
                offers = self.fetch_safe(url) 
                all_results.extend(offers) 
            except Exception:
                self.logger.error(f"Nie udało się pobrać danych z {url} po wszystkich próbach.")
                continue
        return all_results
    
if __name__ == "__main__":
    t = JustJoinIt()
    print(t.fetch_all())