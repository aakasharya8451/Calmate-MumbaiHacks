"""
Blocker Identification Agent

Identifies common blockers preventing progress or causing delays.
Blockers include: waiting for approvals, lack of clarity, resource shortages, etc.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.config import AGENT_SETTINGS
from models.analysis_models import BlockerIdentificationResult


class BlockerFinderAgent(BaseAgent):
    """Agent specialized in identifying blockers"""
    
    def __init__(self):
        settings = AGENT_SETTINGS["blocker_finder"]
        super().__init__(model_name=settings["model"])
        self.temperature = settings["temperature"]
        self.max_tokens = settings["max_tokens"]
    
    def _build_blocker_prompt(self, transcript: list[dict]) -> str:
        """
        Build prompt for blocker identification
        
        Args:
            transcript: List of conversation messages
            
        Returns:
            Formatted prompt
        """
        base_prompt = self._create_prompt(transcript)
        
        instruction = """
Identify COMMON BLOCKERS mentioned in this call that prevent progress or cause frustration.

COMMON BLOCKER TYPES:
- Waiting for approvals (decisions stuck, pending sign-offs)
- Lack of clarity (unclear requirements, ambiguous goals, confusion)
- Resource crunch (insufficient budget, understaffed, missing tools)
- Bureaucracy (excessive processes, red tape, slow systems)
- Communication gaps (information not shared, poor coordination)
- Technical issues (system problems, tool limitations, bugs)
- Dependencies (waiting on others, blocked by other teams)
- Training gaps (lack of knowledge, unclear procedures)
- Access issues (permissions, credentials, availability)

Extract the 3-5 most significant blockers and return them as a comma-separated list.
Use concise, descriptive labels (e.g., "waiting for approvals", "lack of clarity", "resource crunch").

If no clear blockers are identified, return an empty string.

Respond ONLY with valid JSON in this exact format:
{
  "common_blockers": "blocker1, blocker2, blocker3"
}

Do not include any explanation, only the JSON object.
"""
        return base_prompt + "\n\n" + instruction
    
    async def identify_blockers(self, transcript: list[dict]) -> BlockerIdentificationResult:
        """
        Identify blockers from transcript
        
        Args:
            transcript: Call transcript messages
            
        Returns:
            BlockerIdentificationResult with comma-separated blockers
        """
        prompt = self._build_blocker_prompt(transcript)
        
        response_text = await self.generate_response(prompt)
        result_dict = self._parse_json_response(response_text)
        
        return BlockerIdentificationResult(**result_dict)
