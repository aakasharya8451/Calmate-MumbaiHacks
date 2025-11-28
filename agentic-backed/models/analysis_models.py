"""
Pydantic Models for Call Analysis

Models for the multi-agent analysis pipeline including:
- Individual agent outputs
- Aggregated analysis results
- Final call analysis report
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


class SentimentCounts(BaseModel):
    """Sentiment analysis counts"""
    positive: int = Field(ge=0, description="Number of positive sentiment expressions")
    negative: int = Field(ge=0, description="Number of negative sentiment expressions")


class CallAnalysis(BaseModel):
    """Aggregated analysis from all agents"""
    stressed_detected: bool = Field(description="Whether stress indicators were detected")
    sentiment_counts: SentimentCounts = Field(description="Positive and negative sentiment counts")
    top_stressors: str = Field(description="Comma-separated list of top stressors (empty if none)")
    common_blockers: str = Field(description="Comma-separated list of common blockers (empty if none)")
    is_severe_case: bool = Field(description="Whether this case needs urgent attention")


class CallAnalysisReport(BaseModel):
    """Complete call analysis report with metadata"""
    call_id: str = Field(description="Unique call identifier from VAPI")
    call_duration_seconds: float = Field(ge=0, description="Call duration in seconds")
    analysis_timestamp: str = Field(description="ISO timestamp when analysis was performed")
    analysis: CallAnalysis = Field(description="Analysis results from multi-agent pipeline")
    
    @classmethod
    def create(
        cls,
        call_id: str,
        call_duration_seconds: float,
        stressed_detected: bool,
        sentiment_counts: SentimentCounts,
        top_stressors: str,
        common_blockers: str,
        is_severe_case: bool
    ) -> "CallAnalysisReport":
        """
        Factory method to create analysis report
        
        Args:
            call_id: Call ID from VAPI
            call_duration_seconds: Duration of call
            stressed_detected: Stress detection result
            sentiment_counts: Sentiment analysis result
            top_stressors: Identified stressors
            common_blockers: Identified blockers
            is_severe_case: Severity classification result
            
        Returns:
            CallAnalysisReport instance
        """
        return cls(
            call_id=call_id,
            call_duration_seconds=call_duration_seconds,
            analysis_timestamp=datetime.utcnow().isoformat() + "Z",
            analysis=CallAnalysis(
                stressed_detected=stressed_detected,
                sentiment_counts=sentiment_counts,
                top_stressors=top_stressors,
                common_blockers=common_blockers,
                is_severe_case=is_severe_case
            )
        )


# Individual Agent Output Schemas

class StressDetectionResult(BaseModel):
    """Output from stress detector agent"""
    stressed_detected: bool = Field(description="Whether stress was detected")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")


class SentimentAnalysisResult(BaseModel):
    """Output from sentiment analyzer agent"""
    sentiment_counts: SentimentCounts
    
    
class StressorIdentificationResult(BaseModel):
    """Output from stressor finder agent"""
    top_stressors: str = Field(default="", description="Comma-separated stressors (empty if none)")
    

class BlockerIdentificationResult(BaseModel):
    """Output from blocker finder agent"""
    common_blockers: str = Field(default="", description="Comma-separated blockers (empty if none)")
    

class SeverityClassificationResult(BaseModel):
    """Output from severity classifier agent"""
    is_severe_case: bool = Field(description="Whether urgent attention is needed")
    severity_indicators: Optional[list[str]] = Field(None, description="Reasons for severity classification")


class CallReportDB(BaseModel):
    """
    Database schema model for call_reports table.
    Flattens the nested analysis structure for DB insertion.
    """
    call_id: str
    call_duration_seconds: float
    stressed_detected: bool
    sentiment_counts: Dict[str, int]  # Will be stored as JSONB
    top_stressors: Optional[str] = None
    common_blockers: Optional[str] = None
    is_severe_case: bool

    @classmethod
    def from_analysis_report(cls, report: CallAnalysisReport) -> "CallReportDB":
        """
        Convert a CallAnalysisReport to a DB-ready CallReportDB model.
        Handles flattening and type conversions (e.g. lists to strings).
        """
        analysis = report.analysis
        
        # Handle top_stressors (list -> comma-separated string)
        top_stressors_str = None
        if analysis.top_stressors:
            # Check if it's already a string (some agents might return string)
            if isinstance(analysis.top_stressors, str):
                top_stressors_str = analysis.top_stressors
            # If it's a list (as defined in some models), join it
            elif isinstance(analysis.top_stressors, list):
                top_stressors_str = ", ".join(analysis.top_stressors)
            # If it's a string that looks like a list representation (edge case), keep as is
            else:
                top_stressors_str = str(analysis.top_stressors)

        # Handle common_blockers (list -> comma-separated string)
        common_blockers_str = None
        if analysis.common_blockers:
            if isinstance(analysis.common_blockers, str):
                common_blockers_str = analysis.common_blockers
            elif isinstance(analysis.common_blockers, list):
                common_blockers_str = ", ".join(analysis.common_blockers)
            else:
                common_blockers_str = str(analysis.common_blockers)

        return cls(
            call_id=report.call_id,
            call_duration_seconds=report.call_duration_seconds,
            stressed_detected=analysis.stressed_detected,
            sentiment_counts=analysis.sentiment_counts.model_dump(),
            top_stressors=top_stressors_str,
            common_blockers=common_blockers_str,
            is_severe_case=analysis.is_severe_case
        )
