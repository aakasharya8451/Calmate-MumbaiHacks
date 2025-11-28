"""
Processor for Vapi end-of-call-report messages.

This module handles transformation of raw end-of-call-report webhook
data into clean, validated ProcessedCall objects.
"""

from typing import Any, Dict, List, Optional
from models.processed_call import ProcessedCall, TranscriptMessage


def process_end_of_call_report(message: Dict[str, Any]) -> ProcessedCall:
    """
    Process a raw end-of-call-report message into a clean ProcessedCall object.
    
    This function extracts key fields from the flexible webhook message structure
    and transforms them into a validated, clean output format.
    
    Args:
        message: Raw message dictionary from Vapi webhook.
                 Expected to have type "end-of-call-report".
    
    Returns:
        ProcessedCall: Validated processed call data with extracted fields.
    
    Raises:
        ValueError: If message type is not "end-of-call-report" or required
                   fields are missing.
        KeyError: If essential nested fields are not present.
    
    Example:
        >>> raw_message = {
        ...     "type": "end-of-call-report",
        ...     "call": {"id": "123", "type": "webCall"},
        ...     "assistant": {"id": "456"},
        ...     "startedAt": "2025-11-29T06:53:19.677Z",
        ...     "endedAt": "2025-11-29T06:55:00.142Z",
        ...     "durationSeconds": 100.5,
        ...     "messages": [
        ...         {"role": "user", "message": "Hello"},
        ...         {"role": "assistant", "message": "Hi there!"}
        ...     ]
        ... }
        >>> processed = process_end_of_call_report(raw_message)
        >>> processed.call_id
        '123'
    """
    # Validate message type
    msg_type = message.get("type")
    if msg_type != "end-of-call-report":
        raise ValueError(
            f"Expected message type 'end-of-call-report', got '{msg_type}'"
        )
    
    # Extract call information
    call = message.get("call", {})
    if not isinstance(call, dict):
        raise ValueError("Missing or invalid 'call' object in message")
    
    call_id = call.get("id")
    if not call_id:
        raise ValueError("Missing 'call.id' in message")
    
    call_type = call.get("type", "unknown")

    # Extract customer information
    customer = message.get("customer", {})
    customer_number = customer.get("number")
    
    # Extract assistant information
    assistant = message.get("assistant", {})
    if not isinstance(assistant, dict):
        raise ValueError("Missing or invalid 'assistant' object in message")
    
    agent_id = assistant.get("id")
    if not agent_id:
        raise ValueError("Missing 'assistant.id' in message")
    
    # Extract timestamps
    start_timestamp = message.get("startedAt")
    if not start_timestamp:
        raise ValueError("Missing 'startedAt' in message")
    
    end_timestamp = message.get("endedAt")
    if not end_timestamp:
        raise ValueError("Missing 'endedAt' in message")
    
    # Extract duration
    duration_seconds = message.get("durationSeconds")
    if duration_seconds is None:
        raise ValueError("Missing 'durationSeconds' in message")
    
    # Transform messages to simple transcript
    raw_messages = message.get("messages", [])
    transcript = _transform_messages(raw_messages)
    
    # Create and return ProcessedCall (Pydantic validation happens here)
    return ProcessedCall(
        call_id=call_id,
        agent_id=agent_id,
        customer_number=customer_number,
        call_type=call_type,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        duration_seconds=duration_seconds,
        transcript=transcript
    )


def _transform_messages(
    raw_messages: List[Dict[str, Any]]
) -> List[TranscriptMessage]:
    """
    Transform raw message list to simplified transcript format.
    
    Extracts only 'role' and 'message' (renamed to 'content') from each
    message, discarding timing and other metadata.
    
    Args:
        raw_messages: List of raw message dictionaries from Vapi.
                     Each should have 'role' and 'message' fields.
    
    Returns:
        List of TranscriptMessage objects with role and content only.
    """
    transcript = []
    
    for raw_msg in raw_messages:
        if not isinstance(raw_msg, dict):
            continue
        
        role = raw_msg.get("role", "unknown")
        content = raw_msg.get("message", "")
        
        # Only include messages that have content
        if content:
            transcript.append(
                TranscriptMessage(role=role, content=content)
            )
    
    return transcript
