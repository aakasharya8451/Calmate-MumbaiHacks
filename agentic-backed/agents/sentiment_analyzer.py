"""
Sentiment Analysis Agent

Counts positive and negative sentiment expressions in call transcripts.
Positive: hopeful, grateful, satisfied, optimistic, happy
Negative: frustrated, angry, disappointed, sad, discouraged
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.config import AGENT_SETTINGS
from models.analysis_models import SentimentAnalysisResult, SentimentCounts


class SentimentAnalyzerAgent(BaseAgent):
    """Agent specialized in counting sentiment expressions"""
    
    def __init__(self):
        settings = AGENT_SETTINGS["sentiment_analyzer"]
        super().__init__(model_name=settings["model"])
        self.temperature = settings["temperature"]
        self.max_tokens = settings["max_tokens"]
    
    def _build_sentiment_prompt(self, transcript: list[dict]) -> str:
        """
        Build prompt for sentiment analysis
        
        Args:
            transcript: List of conversation messages
            
        Returns:
            Formatted prompt
        """
        base_prompt = self._create_prompt(transcript)
        
        instruction = """
Count the number of POSITIVE and NEGATIVE sentiment expressions in the call transcript.

POSITIVE INDICATORS:
- Hopeful, optimistic expressions
- Gratitude or appreciation
- Satisfaction or contentment
- Excitement or enthusiasm
- Relief or comfort

NEGATIVE INDICATORS:
- Frustration or anger
- Disappointment or discouragement
- Sadness or distress
- Fear or anxiety
- Resignation or hopelessness

Count each distinct expression. If the same sentiment is repeated, count each occurrence.

Respond ONLY with valid JSON in this exact format:
{
  "sentiment_counts": {
    "positive": <number>,
    "negative": <number>
  }
}

Do not include any explanation, only the JSON object.
"""
        return base_prompt + "\n\n" + instruction
    
    async def analyze_sentiment(self, transcript: list[dict]) -> SentimentAnalysisResult:
        """
        Analyze sentiment in transcript
        
        Args:
            transcript: Call transcript messages
            
        Returns:
            SentimentAnalysisResult with positive/negative counts
        """
        prompt = self._build_sentiment_prompt(transcript)
        
        try:
            response_text = await self.generate_response(prompt)
            result_dict = self._parse_json_response(response_text)
            return SentimentAnalysisResult(**result_dict)
            
        except RuntimeError as e:
            if "SAFETY" in str(e):
                print(f"⚠️  Sentiment analysis blocked by safety filters. Using default neutral values.")
                # Return neutral result on safety block
                return SentimentAnalysisResult(
                    sentiment_counts=SentimentCounts(positive=0, negative=0)
                )
            raise e
