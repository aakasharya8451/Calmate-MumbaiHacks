"""
Agent Configuration

Centralized configuration for all agents including:
- Model selection (Flash vs Pro)
- Temperature and generation settings
- Timeout policies
- Retry settings
"""

# Model Configuration
STRESS_DETECTOR_MODEL = "gemini-flash-latest"
SENTIMENT_ANALYZER_MODEL = "gemini-flash-latest"
STRESSOR_FINDER_MODEL = "gemini-flash-latest"
BLOCKER_FINDER_MODEL = "gemini-flash-latest"
SEVERITY_CLASSIFIER_MODEL = "gemini-pro-latest"  # Use Pro for critical decisions

# Generation Parameters
DEFAULT_TEMPERATURE = 0.3  # Lower for more consistent outputs
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT = 30  # seconds

# Retry Configuration
MAX_RETRIES = 2
RETRY_DELAY = 1  # seconds

import google.generativeai as genai

# Safety Settings (Block None)
SAFETY_SETTINGS = [
    {
        "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
    },
    {
        "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
    },
    {
        "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
    },
    {
        "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
    },
]

# Agent-specific settings
AGENT_SETTINGS = {
    "stress_detector": {
        "model": STRESS_DETECTOR_MODEL,
        "temperature": 0.2,  # Very consistent for binary classification
        "max_tokens": 512,
    },
    "sentiment_analyzer": {
        "model": SENTIMENT_ANALYZER_MODEL,
        "temperature": 0.3,
        "max_tokens": 512,
    },
    "stressor_finder": {
        "model": STRESSOR_FINDER_MODEL,
        "temperature": 0.4,  # Slightly higher for creative categorization
        "max_tokens": 1024,
    },
    "blocker_finder": {
        "model": BLOCKER_FINDER_MODEL,
        "temperature": 0.4,
        "max_tokens": 1024,
    },
    "severity_classifier": {
        "model": SEVERITY_CLASSIFIER_MODEL,  # Pro model for critical decision
        "temperature": 0.1,  # Very low for consistent severity classification
        "max_tokens": 512,
    },
}
