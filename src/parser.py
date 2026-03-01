from .models import JobOffer

class JobParser:
    MAPPINGS = {
        'justjoin': {
            'title': 'title',
            'company': 'companyName',
            'city': 'city',
        },
        'nofluff': {
            'title': 'title',
            'company': 'name',
            'city': 'location',
        }
    }

    def parse(self, raw_data: dict, source: str) -> list[JobOffer]:
        mapping = self.MAPPINGS.get(source)
        if not mapping:
            print(f"Błąd: Nie znaleziono mapowania dla źródła: {source}")
            return []

        offers = []
        for item in raw_data:
            raw_id = item.get(mapping['id_key'])
            ext_id = f"{source}_{raw_id}"

            offers.append(JobOffer(
                external_id=ext_id,
                title=item.get(mapping['title'], "No title"),
                company=item.get(mapping['company'], "No company"),
                city=item.get(mapping['city'], "No city"),
                url=item.get('full_url'), 
                source=source             
            ))
        return offers