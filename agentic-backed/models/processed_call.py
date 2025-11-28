"""
Pydantic model for processed call data.

This module defines the output structure for processed end-of-call reports.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class TranscriptMessage(BaseModel):
    """
    A single message in the call transcript.
    
    Attributes:
        role: The role of the message sender (system, user, assistant).
        content: The content/text of the message.
    """
    
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")


class ProcessedCall(BaseModel):
    """
    Processed call data extracted from Vapi end-of-call-report.
    
    This model represents the clean, validated output after processing
    a raw end-of-call-report webhook message.
    
    Attributes:
        call_id: Unique identifier for the call.
        agent_id: Identifier for the AI assistant/agent used.
        call_type: Type of call (webCall, inboundPhoneCall, outboundPhoneCall).
        start_timestamp: ISO format timestamp when call started.
        end_timestamp: ISO format timestamp when call ended.
        duration_seconds: Duration of the call in seconds.
        transcript: List of messages with role and content only.
    """
    
    call_id: str = Field(..., description="Unique call identifier")
    agent_id: str = Field(..., description="AI assistant identifier")
    customer_number: Optional[str] = Field(None, description="Customer phone number (if available)")
    call_type: str = Field(..., description="Type of call")
    start_timestamp: str = Field(..., description="ISO format start time")
    end_timestamp: str = Field(..., description="ISO format end time")
    duration_seconds: float = Field(..., gt=0, description="Call duration in seconds")
    transcript: List[TranscriptMessage] = Field(
        default_factory=list,
        description="Simplified transcript with role and content"
    )
    
    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "call_id": "019ab9c9-c216-744e-b009-3bc3d210f73a",
                "agent_id": "23e8f9a7-aace-4c28-8a8f-be525dc9fd38",
                "customer_number": "+1234567890",
                "call_type": "webCall",
                "start_timestamp": "2025-11-29T06:53:19.677Z",
                "end_timestamp": "2025-11-29T06:55:00.142Z",
                "duration_seconds": 100.465,
                "transcript": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi! How can I help you?"}
                ]
            }
        }
