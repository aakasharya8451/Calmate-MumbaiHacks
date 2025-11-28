"""
Call Analyzer - Main Interface for Multi-Agent Analysis

This module provides the main interface for analyzing VAPI call transcripts
using the Google ADK multi-agent pipeline.

Usage:
    from call_analyzer import analyze_call
    
    analysis_report = await analyze_call(processed_call_data)
"""

from typing import Dict, Any
from agents.orchestrator import OrchestratorAgent
from models.analysis_models import CallAnalysisReport


# Global orchestrator instance (reused across calls)
_orchestrator: OrchestratorAgent = None


def get_orchestrator() -> OrchestratorAgent:
    """
    Get or create the global orchestrator instance
    
    Returns:
        OrchestratorAgent instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


async def analyze_call(processed_call_data: Dict[str, Any]) -> CallAnalysisReport:
    """
    Analyze call using Google ADK multi-agent pipeline
    
    This function takes the processed call data from call_report_processor
    and runs it through the multi-agent analysis pipeline, returning a
    complete analysis report.
    
    Args:
        processed_call_data: Output from call_report_processor with:
            - call_id: str
            - duration_seconds: float
            - transcript: list[dict] with 'role' and 'content'
    
    Returns:
        CallAnalysisReport with complete analysis including:
            - stressed_detected: bool
            - sentiment_counts: {positive: int, negative: int}
            - top_stressors: str (comma-separated)
            - common_blockers: str (comma-separated)
            - is_severe_case: bool
    
    Raises:
        ValueError: If required fields are missing
        RuntimeError: If critical agent failure occurs
    
    Example:
        >>> processed_data = {
        ...     "call_id": "abc123",
        ...     "duration_seconds": 245.5,
        ...     "transcript": [
        ...         {"role": "user", "content": "I'm really stressed..."},
        ...         {"role": "assistant", "content": "I understand..."}
        ...     ]
        ... }
        >>> report = await analyze_call(processed_data)
        >>> print(report.analysis.stressed_detected)
        True
    """
    # Validate required fields
    required_fields = ["call_id", "duration_seconds", "transcript"]
    for field in required_fields:
        if field not in processed_call_data:
            raise ValueError(f"Missing required field: {field}")
    
    call_id = processed_call_data["call_id"]
    duration_seconds = processed_call_data["duration_seconds"]
    transcript = processed_call_data["transcript"]
    
    # Validate transcript format
    if not isinstance(transcript, list) or len(transcript) == 0:
        raise ValueError("Transcript must be a non-empty list")
    
    # Get orchestrator and run analysis
    orchestrator = get_orchestrator()
    analysis_report = await orchestrator.analyze_call(
        call_id=call_id,
        transcript=transcript,
        duration_seconds=duration_seconds
    )
    
    return analysis_report
