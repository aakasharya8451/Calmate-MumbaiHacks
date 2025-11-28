"""
Orchestrator Agent - Parent Agent Coordinator

Coordinates all 5 specialized sub-agents in parallel using Google ADK multi-agent pipeline:
1. Stress Detector Agent
2. Sentiment Analyzer Agent
3. Stressor Finder Agent
4. Blocker Finder Agent
5. Severity Classifier Agent

Uses asyncio for parallel execution to maximize speed.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from agents.stress_detector import StressDetectorAgent
from agents.sentiment_analyzer import SentimentAnalyzerAgent
from agents.stressor_finder import StressorFinderAgent
from agents.blocker_finder import BlockerFinderAgent
from agents.severity_classifier import SeverityClassifierAgent
from models.analysis_models import CallAnalysisReport, SentimentCounts


class OrchestratorAgent:
    """
    Parent agent that coordinates all analysis sub-agents
    
    Executes all 5 agents in parallel for fastest processing,
    then aggregates results into a single CallAnalysisReport.
    """
    
    def __init__(self):
        """Initialize all sub-agents"""
        self.stress_detector = StressDetectorAgent()
        self.sentiment_analyzer = SentimentAnalyzerAgent()
        self.stressor_finder = StressorFinderAgent()
        self.blocker_finder = BlockerFinderAgent()
        self.severity_classifier = SeverityClassifierAgent()
    
    async def analyze_call(
        self,
        call_id: str,
        transcript: list[dict],
        duration_seconds: float
    ) -> CallAnalysisReport:
        """
        Analyze call using all sub-agents in parallel
        
        Args:
            call_id: Unique call identifier from VAPI
            transcript: List of message dicts with 'role' and 'content'
            duration_seconds: Call duration in seconds
            
        Returns:
            CallAnalysisReport with complete analysis
            
        Raises:
            RuntimeError: If critical agents fail
        """
        print(f"🤖 Starting multi-agent analysis for call: {call_id}")
        print(f"   Transcript messages: {len(transcript)}")
        print(f"   Duration: {duration_seconds}s")
        
        # Execute all 5 agents in parallel
        try:
            results = await asyncio.gather(
                self._run_stress_detector(transcript),
                self._run_sentiment_analyzer(transcript),
                self._run_stressor_finder(transcript),
                self._run_blocker_finder(transcript),
                self._run_severity_classifier(transcript, duration_seconds),
                return_exceptions=True  # Don't fail everything if one agent fails
            )
            
            stress_result, sentiment_result, stressor_result, blocker_result, severity_result = results
            
        except Exception as e:
            raise RuntimeError(f"Critical failure in agent orchestration: {e}")
        
        # Handle partial failures
        stressed_detected = self._extract_result(stress_result, "stressed_detected", False)
        sentiment_counts = self._extract_sentiment(sentiment_result)
        top_stressors = self._extract_result(stressor_result, "top_stressors", "")
        common_blockers = self._extract_result(blocker_result, "common_blockers", "")
        is_severe_case = self._extract_result(severity_result, "is_severe_case", False)
        
        # Create final report
        report = CallAnalysisReport.create(
            call_id=call_id,
            call_duration_seconds=duration_seconds,
            stressed_detected=stressed_detected,
            sentiment_counts=sentiment_counts,
            top_stressors=top_stressors,
            common_blockers=common_blockers,
            is_severe_case=is_severe_case
        )
        
        print(f"✅ Analysis complete:")
        print(f"   - Stress detected: {stressed_detected}")
        print(f"   - Sentiment: +{sentiment_counts.positive}/-{sentiment_counts.negative}")
        print(f"   - Severity: {'⚠️  URGENT' if is_severe_case else 'Normal'}")
        
        return report
    
    async def _run_stress_detector(self, transcript: list[dict]):
        """Run stress detector agent"""
        try:
            print("   🔍 Running stress detector...")
            result = await self.stress_detector.detect_stress(transcript)
            print(f"   ✓ Stress detector: {result.stressed_detected}")
            return result
        except Exception as e:
            print(f"   ✗ Stress detector failed: {e}")
            return e
    
    async def _run_sentiment_analyzer(self, transcript: list[dict]):
        """Run sentiment analyzer agent"""
        try:
            print("   😊 Running sentiment analyzer...")
            result = await self.sentiment_analyzer.analyze_sentiment(transcript)
            print(f"   ✓ Sentiment: +{result.sentiment_counts.positive}/-{result.sentiment_counts.negative}")
            return result
        except Exception as e:
            print(f"   ✗ Sentiment analyzer failed: {e}")
            return e
    
    async def _run_stressor_finder(self, transcript: list[dict]):
        """Run stressor finder agent"""
        try:
            print("   📋 Running stressor finder...")
            result = await self.stressor_finder.identify_stressors(transcript)
            print(f"   ✓ Stressors: {result.top_stressors or 'none'}")
            return result
        except Exception as e:
            print(f"   ✗ Stressor finder failed: {e}")
            return e
    
    async def _run_blocker_finder(self, transcript: list[dict]):
        """Run blocker finder agent"""
        try:
            print("   🚧 Running blocker finder...")
            result = await self.blocker_finder.identify_blockers(transcript)
            print(f"   ✓ Blockers: {result.common_blockers or 'none'}")
            return result
        except Exception as e:
            print(f"   ✗ Blocker finder failed: {e}")
            return e
    
    async def _run_severity_classifier(self, transcript: list[dict], duration: float):
        """Run severity classifier agent"""
        try:
            print("   ⚠️  Running severity classifier...")
            result = await self.severity_classifier.classify_severity(transcript, duration)
            print(f"   ✓ Severity: {'URGENT' if result.is_severe_case else 'Normal'}")
            return result
        except Exception as e:
            print(f"   ✗ Severity classifier failed: {e}")
            return e
    
    def _extract_result(
        self,
        result: Any,
        field: str,
        default: Any
    ) -> Any:
        """
        Extract field from result, handling exceptions
        
        Args:
            result: Agent result or exception
            field: Field name to extract
            default: Default value if failed
            
        Returns:
            Extracted value or default
        """
        if isinstance(result, Exception):
            print(f"   ⚠️  Using default for {field} due to agent failure")
            return default
        
        return getattr(result, field, default)
    
    def _extract_sentiment(self, result: Any) -> SentimentCounts:
        """
        Extract sentiment counts, handling exceptions
        
        Args:
            result: Sentiment result or exception
            
        Returns:
            SentimentCounts (default to 0/0 if failed)
        """
        if isinstance(result, Exception):
            print(f"   ⚠️  Using default sentiment counts due to agent failure")
            return SentimentCounts(positive=0, negative=0)
        
        return result.sentiment_counts
