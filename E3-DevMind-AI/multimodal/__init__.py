"""
E3 DevMind AI - Multimodal Intelligence System

Provides comprehensive multimodal processing:
- Voice: Speech-to-text, text-to-speech, meeting transcription
- Vision: Image analysis, screenshot analysis, whiteboard OCR
- Video: Meeting analysis, frame extraction, demo processing

All processing flows through ANLT for CSDL integration.
"""

from multimodal.multimodal_processor import MultimodalProcessor
from multimodal.voice.voice_processor import VoiceProcessor
from multimodal.vision.vision_processor import VisionProcessor
from multimodal.video.video_processor import VideoProcessor

__all__ = [
    "MultimodalProcessor",
    "VoiceProcessor",
    "VisionProcessor",
    "VideoProcessor",
]
