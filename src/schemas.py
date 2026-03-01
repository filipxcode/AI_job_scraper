from pydantic import BaseModel, Field

class InputLLM(BaseModel):
    title: str
    company: str
    skills: list[str]
    description: str  
    experience: str | None = "Nie określono"
    location: str | None  = "Zdalnie/Biuro"

    def to_prompt_string(self) -> str:
        skills_str = ", ".join(self.skills)
        return f"""
        STANOWISKO: {self.title}
        FIRMA: {self.company}
        WYMAGANE SKILLS: {skills_str}
        LOKALIZACJA: {self.location}
        POZIOM: {self.experience}
        OPIS: {self.description[:1500]}... (skrócono dla oszczędności)
        """
    
class JobOfferBase(BaseModel):
    title: str
    company: str
    city: str | None = None
    url: str
    source: str
    skills: str
    ai_score: int | None = Field(None, ge=1, le=10) # Od razu zabezpieczamy ocenę!
    ai_summary: str | None = None

class ReasoningLLMOutput(BaseModel):
    analysis: str = Field(
        description="Pełna, opisowa analiza profilu kandydata względem wymagań oferty. Wypisz za i przeciw, porównaj technologie."
    )

class ExtractorLLMOutput(BaseModel):
    score: int = Field(
        ge=1, le=10, 
        description="Ostateczna, liczbowa ocena dopasowania na podstawie wcześniejszej analizy."
    )
    summary: str = Field(
        description="Krótkie uzasadnienie (1-2 zdania) dla użytkownika na Telegram."
    )