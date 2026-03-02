import os
import requests 
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_fixed
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def _env_csv(name: str, default: list[str]) -> list[str]:
    """Read a comma-separated env var into a list of strings."""
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    return [part.strip() for part in raw.split(",") if part.strip()]


def _env_int(name: str, default: int) -> int:
    """Read an int env var; fall back to default if missing/invalid."""
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default

class BaseScraper(ABC):
    def __init__(self):
        """Base class for job board scrapers."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_safe(self, url, *args, **kwargs):
        """Fetch data with retries and basic error logging."""
        self.logger.info(f"Fetching: {url}")
        try:
            return self.get_data(url, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error while fetching {url}: {e}")
            raise
        
    @abstractmethod
    def get_data(self, url, *args, **kwargs):
        pass

class JustJoinIt(BaseScraper):
    BASE_URL = "https://justjoin.it/api/candidate-api/"
    OFFER_FRONTEND_URL = "https://justjoin.it/offers/"

    def __init__(self):
        super().__init__()
        self.categories = _env_csv("JJI_CATEGORIES", ["ai", "python", "data"])
        self.experience_levels = _env_csv("JJI_EXPERIENCE_LEVELS", ["junior"])
        self.limit = _env_int("JJI_ITEMS_COUNT", 50)
        self.from_offset = _env_int("JJI_FROM", 0)

        experience_levels_q = ",".join(self.experience_levels)
        self.urls = [
            f"{self.BASE_URL}offers?categories={cat}&experienceLevels={experience_levels_q}&itemsCount={self.limit}&from={self.from_offset}"
            for cat in self.categories
        ]
    
    def get_data(self, url) -> list[dict]:
        """Fetch JustJoin.it offers JSON."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])

    def fetch_all(self):
        """Fetch and normalize offers for all configured categories."""
        all_results = []
        for url in self.urls:
            try:
                offers = self.fetch_safe(url)
                # Dodajemy pełny link do każdej oferty
                for offer in offers:
                    offer['full_url'] = f"{self.OFFER_FRONTEND_URL}{offer.get('slug')}"
                    offer['source'] = 'justjoin'
                all_results.extend(offers) 
            except Exception:
                continue
        return all_results

class NoFluffJobs(BaseScraper):
    API_URL = "https://nofluffjobs.com/api/search/posting?sort=newest&pageSize=20&salaryCurrency=PLN&salaryPeriod=month&region=pl"
    OFFER_FRONTEND_URL = "https://nofluffjobs.com/job/"

    def __init__(self):
        super().__init__()
        raw_search = os.getenv("NFJ_RAW_SEARCH", "junior python")
        categories = _env_csv("NFJ_CATEGORY", ["artificial-intelligence"])
        developer_status = _env_csv("NFJ_DEVELOPER_STATUS", ["junior"])

        self.payload = {
            "rawSearch": raw_search,
            "common": {
                "category": categories,
                "developerStatus": developer_status,
            }
        }

    def get_data(self, url, payload=None) -> list[dict]:
        """Fetch NoFluffJobs postings JSON."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json().get('postings', [])

    def _is_remote_variant(self, offer: dict) -> bool:
        """Detect whether the offer represents a fully-remote variant."""
        location = offer.get("location")
        if isinstance(location, dict) and location.get("fullyRemote") is True:
            return True

        places = location.get("places") if isinstance(location, dict) else None
        if isinstance(places, list):
            for p in places:
                if isinstance(p, dict) and p.get("city") == "Remote":
                    return True
        return False

    def _dedupe_offers(self, offers: list[dict]) -> list[dict]:
        """De-duplicate postings, preferring remote variants when available."""
        best_by_key: dict[str, dict] = {}
        for offer in offers:
            if not isinstance(offer, dict):
                continue

            key = offer.get("reference") or offer.get("id")
            if key is None:
                key = offer.get("full_url") or offer.get("url")
            key = str(key)

            current = best_by_key.get(key)
            if current is None:
                best_by_key[key] = offer
                continue
            if self._is_remote_variant(offer) and not self._is_remote_variant(current):
                best_by_key[key] = offer

        return list(best_by_key.values())

    def fetch_all(self):
        """Fetch, normalize and de-duplicate NoFluffJobs offers."""
        try:
            offers = self.fetch_safe(self.API_URL, payload=self.payload)
            for offer in offers:
                slug = offer.get('url')
                offer['full_url'] = f"{self.OFFER_FRONTEND_URL}{slug}"
                offer['source'] = 'nofluffjobs'
            return self._dedupe_offers(offers)
        except Exception:
            self.logger.error("Failed to fetch data from NoFluffJobs")
            return []