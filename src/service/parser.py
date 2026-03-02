import logging
from ..schemas.schemas import JobOfferCreate

logger = logging.getLogger(__name__)
class JobParser:
    MAPPINGS = {
        'justjoin': {
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

    def _nofluff_city(self, item: dict) -> str | None:
        location = item.get("location")
        if not isinstance(location, dict):
            return None

        places = location.get("places")
        if not isinstance(places, list) or not places:
            return None

        # Prefer explicit Remote if present
        for p in places:
            if isinstance(p, dict) and (p.get("city") == "Remote"):
                return "Remote"

        first = places[0]
        if isinstance(first, dict):
            return first.get("city")
        return None

    def _nofluff_skills_to_string(self, item: dict) -> str:
        tiles = item.get("tiles")
        values = tiles.get("values") if isinstance(tiles, dict) else None
        values = values if isinstance(values, list) else []

        required = [v.get("value") for v in values if isinstance(v, dict) and v.get("type") == "requirement" and v.get("value")]
        nice: list[str] = []

        primary = item.get("technology")
        if isinstance(primary, str) and primary and primary not in required:
            required = [primary, *required]

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

            if source == "nofluffjobs":
                title = item.get("title") or "No title"
                company = item.get("name") or "No company"
                city = self._nofluff_city(item)
                skills_str = self._nofluff_skills_to_string(item)
            else:
                mapping = self.MAPPINGS.get(source)
                if not mapping:
                    logger.info(f"Błąd: Nie znaleziono mapowania dla źródła: {source}")
                    continue

                title = item.get(mapping['title'], "No title")
                company = item.get(mapping['company'], "No company")
                city = item.get(mapping['city'])
                skills_str = self._skills_to_string(item, mapping)

            url = item.get('full_url') or item.get('url') or ""
            if not url:
                logger.warning("Pominięto ofertę bez URL")
                continue
            
            offers.append(
                JobOfferCreate(
                    title=title,
                    company=company,
                    city=city,
                    url=url,
                    skills=skills_str,
                    source=source or "unknown",
                )
            )

        return offers