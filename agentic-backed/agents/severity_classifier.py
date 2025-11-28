"""
Severity Classification Agent

Determines if a call represents a severe case requiring urgent attention.
Severe cases include: crisis situations, self-harm risk, extreme distress, immediate danger.

Uses Gemini Pro model for higher accuracy on this critical decision.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.config import AGENT_SETTINGS
from models.analysis_models import SeverityClassificationResult


class SeverityClassifierAgent(BaseAgent):
    """Agent specialized in severity classification - uses Pro model for critical decisions"""
    
    def __init__(self):
        settings = AGENT_SETTINGS["severity_classifier"]
        super().__init__(model_name=settings["model"])  # Uses Pro model
        self.temperature = settings["temperature"]
        self.max_tokens = settings["max_tokens"]
    
    def _build_severity_prompt(self, transcript: list[dict], duration: float) -> str:
        """
        Build prompt for severity classification
        
        Args:
            transcript: List of conversation messages
            duration: Call duration in seconds
            
        Returns:
            Formatted prompt
        """
        base_prompt = self._create_prompt(transcript, duration)
        
        instruction = """
Determine if this call represents a SEVERE CASE requiring URGENT attention.

SEVERE CASE INDICATORS (any of these = severe):
- Self-harm mentions or suicidal ideation
- Immediate danger to self or others
- Extreme emotional distress (panic attack, breakdown, crisis)
- Mentions of abuse or violence
- Severe mental health crisis
- Expressions of giving up or losing hope entirely
- Plans to harm self or others

NON-SEVERE (typical stress/difficulty):
- General work stress or frustration
- Relationship conflicts
- Financial concerns
- Time management issues
- Typical anxiety or worry

Also consider call duration as context:
- Very short calls (<60s) with crisis language = likely severe
- Long calls (>300s) exploring options = may be less severe

Respond ONLY with valid JSON in this exact format:
{
  "is_severe_case": true or false,
  "severity_indicators": ["reason1", "reason2"] or null
}

If is_severe_case is true, provide the specific indicators found. If false, set severity_indicators to null.

Do not include any explanation, only the JSON object.
"""
        return base_prompt + "\n\n" + instruction
    
    async def classify_severity(
        self, 
        transcript: list[dict],
        duration: float
    ) -> SeverityClassificationResult:
        """
        Classify severity of case
        
        Args:
            transcript: Call transcript messages
            duration: Call duration in seconds
            
        Returns:
            SeverityClassificationResult with boolean and indicators
        """
        prompt = self._build_severity_prompt(transcript, duration)
        
        response_text = await self.generate_response(prompt)
        result_dict = self._parse_json_response(response_text)
        
        return SeverityClassificationResult(**result_dict)
