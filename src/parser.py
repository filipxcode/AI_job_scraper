import logging
from .schemas import JobOfferCreate

logger = logging.getLogger(__name__)
class JobParser:
    MAPPINGS = {
        'justjoin': {
            'title': 'title',
            'company': 'companyName',
            'city': 'city',
            'skills':'requiredSkills',
            'nice_to_have':'niceToHaveSkills'
        },
        'nofluffjobs': {
            'title': 'title',
            'company': 'companyName',
            'city': 'city',
            'skills':'requiredSkills',
            'nice_to_have':'niceToHaveSkills'
        }
    }
    
    def _skills_to_string(self, item: dict, mapping: dict) -> str:
        required = item.get(mapping['skills']) or []
        nice = item.get(mapping['nice_to_have']) or []
        return f"REQUIRED: {required}\nNICE_TO_HAVE: {nice}"
    
    def parse(self, raw_data: list[dict]) -> list[JobOfferCreate]:
        if not isinstance(raw_data, list):
            logger.warning(f"Parser dostał {type(raw_data)=}, oczekiwano list[dict].")
            return []

        offers: list[JobOfferCreate] = []

        for item in raw_data:
            if not isinstance(item, dict):
                logger.warning(f"Pominięto rekord o typie {type(item)=}: {item!r}")
                continue

            source = item.get("source")
            mapping = self.MAPPINGS.get(source)
            if not mapping:
                logger.info(f"Błąd: Nie znaleziono mapowania dla źródła: {source}")
                continue

            skills_str = self._skills_to_string(item, mapping)

            url = item.get('full_url') or item.get('url') or ""
            if not url:
                logger.warning("Pominięto ofertę bez URL")
                continue

            offers.append(
                JobOfferCreate(
                    title=item.get(mapping['title'], "No title"),
                    company=item.get(mapping['company'], "No company"),
                    city=item.get(mapping['city']),
                    url=url,
                    skills=skills_str,
                    source=source or "unknown",
                )
            )

        return offers