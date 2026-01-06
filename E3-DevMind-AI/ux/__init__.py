"""
User Experience Enhancement Module

Provides consistent, high-quality user experiences across the E3-DevMind-AI system.
"""

from .response_formatter import ResponseFormatter
from .confidence_scorer import ConfidenceScorer
from .metadata_enhancer import MetadataEnhancer
from .error_handler import UserFriendlyErrorHandler
from .presentation import PresentationEngine

__all__ = [
    "ResponseFormatter",
    "ConfidenceScorer",
    "MetadataEnhancer",
    "UserFriendlyErrorHandler",
    "PresentationEngine"
]
