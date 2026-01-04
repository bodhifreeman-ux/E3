"""
Multimodal Intelligence Integration

Unified interface for all multimodal processing in E3 DevMind AI.
Coordinates voice, vision, and video processing.
"""

from typing import Dict, Any, Optional, List
import structlog
from pathlib import Path

from multimodal.voice.voice_processor import VoiceProcessor
from multimodal.vision.vision_processor import VisionProcessor
from multimodal.video.video_processor import VideoProcessor

logger = structlog.get_logger()


class MultimodalProcessor:
    """
    Unified multimodal processing interface

    Integrates:
    - Voice processing (speech-to-text, text-to-speech)
    - Vision processing (image analysis, OCR)
    - Video processing (meeting analysis, frame extraction)

    All processing flows through ANLT for CSDL integration
    """

    def __init__(self, openai_api_key: str, anlt_client):
        """
        Initialize Multimodal Processor

        Args:
            openai_api_key: OpenAI API key for Whisper, TTS, and GPT-4V
            anlt_client: ANLT client for CSDL translation
        """
        logger.info("initializing_multimodal_processor")

        # Initialize individual processors
        self.voice = VoiceProcessor(openai_api_key, anlt_client)
        self.vision = VisionProcessor(openai_api_key, anlt_client)
        self.video = VideoProcessor(self.voice, self.vision, anlt_client)

        self.anlt = anlt_client

        logger.info("multimodal_processor_initialized",
                   processors=["voice", "vision", "video"])

    async def process_input(
        self,
        input_path: str,
        input_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Automatically detect and process multimodal input

        Args:
            input_path: Path to input file
            input_type: Optional type hint (voice/vision/video)
            **kwargs: Additional arguments for specific processor

        Returns:
            Dict containing processed results in CSDL format
        """
        logger.info("processing_multimodal_input",
                   path=input_path,
                   type=input_type)

        try:
            # Auto-detect input type if not provided
            if input_type is None:
                input_type = self._detect_input_type(input_path)

            logger.info("detected_input_type", type=input_type)

            # Route to appropriate processor
            if input_type == "voice":
                return await self.voice.process_voice_input(input_path, **kwargs)

            elif input_type == "vision":
                query = kwargs.get("query", "Analyze this image")
                image_type = kwargs.get("image_type", "general")
                return await self.vision.analyze_image(input_path, query, image_type)

            elif input_type == "video":
                return await self.video.process_meeting_video(input_path, **kwargs)

            else:
                raise ValueError(f"Unknown input type: {input_type}")

        except Exception as e:
            logger.error("multimodal_processing_failed",
                        error=str(e),
                        path=input_path)
            return {
                "status": "error",
                "error": str(e),
                "input_path": input_path
            }

    def _detect_input_type(self, input_path: str) -> str:
        """
        Auto-detect input type from file extension

        Args:
            input_path: Path to input file

        Returns:
            Input type (voice/vision/video)
        """
        path = Path(input_path)
        suffix = path.suffix.lower()

        # Voice formats
        if suffix in [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"]:
            return "voice"

        # Image formats
        if suffix in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]:
            return "vision"

        # Video formats
        if suffix in [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"]:
            return "video"

        logger.warning("unknown_file_format", suffix=suffix, path=input_path)
        raise ValueError(f"Unsupported file format: {suffix}")

    async def process_meeting(
        self,
        meeting_file: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process E3 meeting (audio or video)

        Args:
            meeting_file: Path to meeting recording
            language: Meeting language

        Returns:
            Dict containing comprehensive meeting analysis
        """
        logger.info("processing_meeting", file=meeting_file, language=language)

        input_type = self._detect_input_type(meeting_file)

        if input_type == "voice":
            return await self.voice.transcribe_meeting(meeting_file, language)
        elif input_type == "video":
            return await self.video.process_meeting_video(meeting_file, language)
        else:
            raise ValueError(f"Invalid meeting file type: {input_type}")

    async def generate_response(
        self,
        csdl_response: Dict[str, Any],
        output_format: str = "voice",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate multimodal output from CSDL response

        Args:
            csdl_response: CSDL formatted response
            output_format: Output format (voice/text)
            **kwargs: Additional arguments for output generation

        Returns:
            Dict containing generated output
        """
        logger.info("generating_multimodal_response", format=output_format)

        try:
            if output_format == "voice":
                voice = kwargs.get("voice", "nova")
                speed = kwargs.get("speed", 1.0)
                return await self.voice.generate_voice_output(
                    csdl_response,
                    voice=voice,
                    speed=speed
                )

            elif output_format == "text":
                text = await self.anlt.csdl_to_text(csdl_response)
                return {
                    "text": text,
                    "status": "success"
                }

            else:
                raise ValueError(f"Unknown output format: {output_format}")

        except Exception as e:
            logger.error("response_generation_failed", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }

    async def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Quick screenshot analysis

        Args:
            screenshot_path: Path to screenshot

        Returns:
            Dict containing screenshot analysis
        """
        return await self.vision.analyze_screenshot(screenshot_path)

    async def extract_whiteboard(self, whiteboard_path: str) -> Dict[str, Any]:
        """
        Quick whiteboard extraction

        Args:
            whiteboard_path: Path to whiteboard image

        Returns:
            Dict containing extracted content
        """
        return await self.vision.extract_whiteboard(whiteboard_path)

    async def transcribe_voice(
        self,
        audio_path: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Quick voice transcription

        Args:
            audio_path: Path to audio file
            language: Audio language

        Returns:
            Dict containing transcription
        """
        return await self.voice.process_voice_input(audio_path, language)

    async def batch_process(
        self,
        input_files: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple files in batch

        Args:
            input_files: List of file paths
            **kwargs: Additional arguments for processing

        Returns:
            List of processing results
        """
        logger.info("batch_processing", file_count=len(input_files))

        results = []

        for file_path in input_files:
            result = await self.process_input(file_path, **kwargs)
            results.append(result)

        successful = sum(1 for r in results if r.get("status") == "success")

        logger.info("batch_processing_complete",
                   total=len(results),
                   successful=successful,
                   failed=len(results) - successful)

        return results

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get multimodal processor capabilities

        Returns:
            Dict describing all capabilities
        """
        return {
            "voice": {
                "speech_to_text": True,
                "text_to_speech": True,
                "meeting_transcription": True,
                "languages": self.voice.supported_languages,
                "voices": self.voice.voice_options
            },
            "vision": {
                "image_analysis": True,
                "screenshot_analysis": True,
                "whiteboard_ocr": True,
                "code_extraction": True,
                "ui_review": True,
                "formats": self.vision.supported_formats
            },
            "video": {
                "meeting_analysis": True,
                "demo_analysis": True,
                "frame_extraction": True,
                "audio_extraction": True,
                "formats": self.video.supported_formats
            }
        }
