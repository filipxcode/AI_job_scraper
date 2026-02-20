from dataclasses import dataclass

@dataclass
class JobOffer:
    title: str
    company: str
    salary_from: int | None
    salary_to: int | None
    url: str
    source: str  