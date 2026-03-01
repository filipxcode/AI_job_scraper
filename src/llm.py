import logging
from .prompts import PromptOrganizer
from .settings import LLMFactory
from .schemas import ReasoningLLMOutput, ExtractorLLMOutput

logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self):
        self.model = LLMFactory.get_llm()
        
        self.reasoning_chain = self.model.with_structured_output(ReasoningLLMOutput)
        self.extraction_chain = self.model.with_structured_output(ExtractorLLMOutput)

    def _run_reasoning_step(self, candidate_data: str, job_data_str: str) -> str:
        messages = [
            SystemMessage(content=PromptOrganizer.REASONING_SYSTEM),
            HumanMessage(content=PromptOrganizer.reasoning_user(
                candidate_data=candidate_data, 
                job_offer=job_data_str
            ))
        ]
        response = self.reasoning_chain.invoke(messages)
        return response.analysis

    def _run_extraction_step(self, candidate_data: str, hr_analysis: str) -> ExtractorLLMOutput:
        messages = [
            SystemMessage(content=PromptOrganizer.EXTRACT_SKILLS_SYSTEM),
            HumanMessage(content=PromptOrganizer.extract_skills_user(
                candidate_data=candidate_data, 
                hr_analysis=hr_analysis
            ))
        ]
        return self.extraction_chain.invoke(messages)

    def process_query(self, candidate_data: str, job_data: dict) -> ExtractorLLMOutput | None:
        
        job_data_str = str(job_data) 
        
        try:
            logger.info(f"Rozpoczynam analizę oferty: {job_data.get('title', 'Nieznana')}")

            hr_analysis = self._run_reasoning_step(candidate_data, job_data_str)
            logger.debug("Zakończono krok 1: Reasoning.")
            
            final_result = self._run_extraction_step(candidate_data, hr_analysis)
            logger.info(f"Zakończono ocenę. Wynik: {final_result.score}/10")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania oferty przez LLM: {e}")
            return None