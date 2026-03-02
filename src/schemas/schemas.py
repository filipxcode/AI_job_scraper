from pydantic import BaseModel, Field


class JobOfferCreate(BaseModel):
    title: str
    company: str
    city: str | None = None
    url: str
    source: str
    skills: str

class JobOfferBase(BaseModel):
    title: str
    company: str
    city: str | None = None
    url: str
    source: str
    skills: str
    ai_score: int | None = Field(None, ge=1, le=10)
    ai_summary: str | None = None
    class Config:
        from_attributes = True

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