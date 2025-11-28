"""
Base Agent Configuration and Utilities

Shared configuration for all Google ADK agents including:
- Gemini API client initialization
- Common prompt templates
- Error handling wrappers
- Response parsing utilities
"""

import os
import json
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


def _get_api_key() -> str:
    """
    Get Google API key from environment
    
    Returns:
        API key string
        
    Raises:
        ValueError: If GOOGLE_API_KEY not found
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables.\n"
            "Please create a .env file with your Google API key.\n"
            "Get your API key from: https://makersuite.google.com/app/apikey\n"
            "Example .env content:\n"
            "GOOGLE_API_KEY=your_actual_api_key_here"
        )
    return api_key


# Configuration will be lazy-loaded when first agent is created
_api_configured = False


def _configure_api():
    """Configure Gemini API (called lazily on first use)"""
    global _api_configured
    if not _api_configured:
        api_key = _get_api_key()
        genai.configure(api_key=api_key)
        _api_configured = True


class AgentConfig:
    """Configuration for agent models"""
    
    # Model selection
    FLASH_MODEL = os.getenv("AGENT_MODEL", "gemini-1.5-flash")
    PRO_MODEL = "gemini-1.5-pro"
    
    # Generation parameters
    TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "1024"))
    TIMEOUT = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    
    # Generation config
    GENERATION_CONFIG = {
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_TOKENS,
    }


class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, model_name: str = None, safety_settings: list[dict] = None):
        """
        Initialize agent with specified model
        
        Args:
            model_name: Gemini model to use (default: flash from config)
            safety_settings: Safety settings list (default: from config)
        """
        # Configure API on first agent creation
        _configure_api()
        
        if model_name is None:
            model_name = AgentConfig.FLASH_MODEL
            
        if safety_settings is None:
            # Import here to avoid circular import if config imports base_agent
            from agents.config import SAFETY_SETTINGS
            safety_settings = SAFETY_SETTINGS
            
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=safety_settings
        )
        
    def _create_prompt(self, transcript: list[dict], duration: Optional[int] = None) -> str:
        """
        Create formatted prompt from transcript
        
        Args:
            transcript: List of messages with 'role' and 'content'
            duration: Optional call duration in seconds
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add transcript
        prompt_parts.append("CALL TRANSCRIPT:")
        for msg in transcript:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        
        # Add duration if provided
        if duration:
            prompt_parts.append(f"\nCALL DURATION: {duration} seconds")
        
        return "\n".join(prompt_parts)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from model response
        
        Args:
            response_text: Raw response from model
            
        Returns:
            Parsed JSON dict
            
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Try to extract JSON from code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate response from model
        
        Args:
            prompt: Input prompt
            
        Returns:
            Model response text
            
        Raises:
            RuntimeError: If API call fails or response is blocked
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=AgentConfig.GENERATION_CONFIG
            )
            
            # Check if response was blocked or empty
            if not response.candidates:
                raise RuntimeError(
                    f"No response candidates returned. "
                    f"Likely blocked by safety filters."
                )
            
            candidate = response.candidates[0]
            
            # Check finish reason
            # 1 = STOP (normal completion), anything else is an error
            if candidate.finish_reason != 1:
                finish_reasons = {
                    2: "SAFETY - Response blocked by safety filters",
                    3: "RECITATION - Response blocked due to recitation",
                    4: "OTHER - Response stopped for other reasons"
                }
                reason = finish_reasons.get(candidate.finish_reason, f"Unknown ({candidate.finish_reason})")
                raise RuntimeError(reason)
            
            # Safely access text
            if not candidate.content or not candidate.content.parts:
                raise RuntimeError("Response has no content parts")
            
            return response.text
            
        except Exception as e:
            # Re-raise if already a RuntimeError with our custom message
            if isinstance(e, RuntimeError):
                raise RuntimeError(f"Agent {self.model_name} failed: {e}")
            # Wrap other exceptions
            raise RuntimeError(f"Agent {self.model_name} failed: {e}") from e


def format_transcript_for_display(transcript: list[dict]) -> str:
    """
    Format transcript for readable display
    
    Args:
        transcript: List of message dicts
        
    Returns:
        Formatted transcript string
    """
    lines = []
    for msg in transcript:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)
