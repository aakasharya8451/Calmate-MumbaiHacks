"""
Stress Detection Agent

Analyzes call transcripts to detect stress indicators including:
- Anxiety and worry expressions
- Frustration and overwhelm
- Time pressure and urgency
- Emotional distress markers
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentConfig
from agents.config import AGENT_SETTINGS
from models.analysis_models import StressDetectionResult


class StressDetectorAgent(BaseAgent):
    """Agent specialized in detecting stress from call transcripts"""
    
    def __init__(self):
        settings = AGENT_SETTINGS["stress_detector"]
        super().__init__(model_name=settings["model"])
        self.temperature = settings["temperature"]
        self.max_tokens = settings["max_tokens"]
    
    def _build_stress_detection_prompt(self, transcript: list[dict]) -> str:
        """
        Build prompt for stress detection
        
        Args:
            transcript: List of conversation messages
            
        Returns:
            Formatted prompt
        """
        base_prompt = self._create_prompt(transcript)
        
        instruction = """
Analyze the above call transcript and determine if the caller is experiencing stress.

STRESS INDICATORS include:
- Words expressing anxiety, worry, or fear
- Expressions of frustration or feeling overwhelmed
- Mentions of time pressure, urgency, or deadlines
- Emotional language (scared, panicking, breaking down)
- Difficulty coping or managing situations
- Sleep problems, exhaustion, burnout

Respond ONLY with valid JSON in this exact format:
{
  "stressed_detected": true or false,
  "confidence": 0.0 to 1.0
}

Do not include any explanation, only the JSON object.
"""
        return base_prompt + "\n\n" + instruction
    
    async def detect_stress(self, transcript: list[dict]) -> StressDetectionResult:
        """
        Detect stress from transcript
        
        Args:
            transcript: Call transcript messages
            
        Returns:
            StressDetectionResult with boolean and confidence
        """
        prompt = self._build_stress_detection_prompt(transcript)
        
        response_text = await self.generate_response(prompt)
        result_dict = self._parse_json_response(response_text)
        
        return StressDetectionResult(**result_dict)
