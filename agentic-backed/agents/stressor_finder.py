"""
Stressor Identification Agent

Identifies and categorizes the top stressors mentioned in call transcripts.
Categories may include: work, relationships, health, finances, time, family, etc.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.config import AGENT_SETTINGS
from models.analysis_models import StressorIdentificationResult


class StressorFinderAgent(BaseAgent):
    """Agent specialized in identifying stressors"""
    
    def __init__(self):
        settings = AGENT_SETTINGS["stressor_finder"]
        super().__init__(model_name=settings["model"])
        self.temperature = settings["temperature"]
        self.max_tokens = settings["max_tokens"]
    
    def _build_stressor_prompt(self, transcript: list[dict]) -> str:
        """
        Build prompt for stressor identification
        
        Args:
            transcript: List of conversation messages
            
        Returns:
            Formatted prompt
        """
        base_prompt = self._create_prompt(transcript)
        
        instruction = """
Identify the TOP STRESSORS mentioned or implied in this call transcript.

COMMON STRESSOR CATEGORIES:
- Workload (too much work, unrealistic expectations)
- Deadlines (time pressure, urgent tasks)
- Management (difficult boss, lack of support, micromanagement)
- Relationships (conflicts, difficult colleagues, isolation)
- Health (physical health issues, sleep problems, exhaustion)
- Finances (money concerns, compensation issues)
- Work-life balance (long hours, no personal time)
- Uncertainty (job security, unclear expectations, changes)
- Resources (lack of tools, insufficient staffing, training gaps)

Extract the 3-5 most prominent stressors and return them as a comma-separated list.
Use concise, descriptive labels (e.g., "workload", "deadlines", "manager behavior").

If no clear stressors are identified, return an empty string.

Respond ONLY with valid JSON in this exact format:
{
  "top_stressors": "stressor1, stressor2, stressor3"
}

Do not include any explanation, only the JSON object.
"""
        return base_prompt + "\n\n" + instruction
    
    async def identify_stressors(self, transcript: list[dict]) -> StressorIdentificationResult:
        """
        Identify stressors from transcript
        
        Args:
            transcript: Call transcript messages
            
        Returns:
            StressorIdentificationResult with comma-separated stressors
        """
        prompt = self._build_stressor_prompt(transcript)
        
        response_text = await self.generate_response(prompt)
        result_dict = self._parse_json_response(response_text)
        
        return StressorIdentificationResult(**result_dict)
