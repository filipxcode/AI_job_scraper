import logging
from .prompts import PromptOrganizer
from ..config.settings import LLMFactory
from ..schemas.schemas import ReasoningLLMOutput, ExtractorLLMOutput
from langchain_core.messages import SystemMessage, HumanMessage
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self):
        """LLM-based processor that scores and summarizes job offers."""
        self.model = LLMFactory.get_llm()
        
        self.reasoning_chain = self.model.with_structured_output(ReasoningLLMOutput)
        self.extraction_chain = self.model.with_structured_output(ExtractorLLMOutput)

    def _run_reasoning_step(self, candidate_data: str, job_data_str: str) -> str:
        """Run the first (reasoning) step and return the raw analysis text."""
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
        """Run the second step to extract structured scoring output."""
        messages = [
            SystemMessage(content=PromptOrganizer.EXTRACT_SKILLS_SYSTEM),
            HumanMessage(content=PromptOrganizer.extract_skills_user(
                candidate_data=candidate_data, 
                hr_analysis=hr_analysis
            ))
        ]
        return self.extraction_chain.invoke(messages)

    def process_query(self, candidate_data: str, job_data: dict) -> ExtractorLLMOutput | None:
        """Score a single job offer. Returns None on failure."""
        
        job_data_str = str(job_data) 
        
        try:
            logger.info(f"Starting offer analysis: {job_data.get('title', 'Unknown')}")

            hr_analysis = self._run_reasoning_step(candidate_data, job_data_str)
            logger.debug("Completed step 1: reasoning")
            
            final_result = self._run_extraction_step(candidate_data, hr_analysis)
            logger.info(f"Scoring complete. Result: {final_result.score}/10")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error while processing offer with LLM: {e}")
            return None