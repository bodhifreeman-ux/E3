"""
Video Intelligence Module

Handles video processing for E3 DevMind AI.
Provides meeting recording analysis, demo video understanding, and frame extraction.
"""

import cv2
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import structlog
from datetime import datetime
import asyncio

logger = structlog.get_logger()


class VideoProcessor:
    """
    Video processing for E3 DevMind AI

    Capabilities:
    - Meeting recording analysis
    - Demo video understanding
    - Frame extraction and key moment identification
    - Audio extraction from video
    - Video summarization
    - Action item extraction from meetings
    """

    def __init__(self, voice_processor, vision_processor, anlt_client):
        """
        Initialize Video Processor

        Args:
            voice_processor: VoiceProcessor instance for audio analysis
            vision_processor: VisionProcessor instance for frame analysis
            anlt_client: ANLT client for CSDL translation
        """
        self.voice = voice_processor
        self.vision = vision_processor
        self.anlt = anlt_client

        self.supported_formats = [
            ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"
        ]

        logger.info("video_processor_initialized",
                   supported_formats=len(self.supported_formats))

    def _validate_video(self, video_path: str) -> bool:
        """
        Validate video file

        Args:
            video_path: Path to video file

        Returns:
            True if valid, False otherwise
        """
        path = Path(video_path)

        if not path.exists():
            logger.error("video_not_found", path=video_path)
            return False

        if path.suffix.lower() not in self.supported_formats:
            logger.error("unsupported_video_format",
                        path=video_path,
                        format=path.suffix)
            return False

        return True

    def extract_frames(
        self,
        video_path: str,
        interval_seconds: int = 30,
        max_frames: int = 20,
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Extract key frames from video

        Args:
            video_path: Path to video file
            interval_seconds: Interval between frames in seconds
            max_frames: Maximum number of frames to extract
            output_dir: Directory to save frames (default: temp directory)

        Returns:
            List of paths to extracted frame images
        """
        logger.info("extracting_frames",
                   video=video_path,
                   interval=interval_seconds,
                   max_frames=max_frames)

        try:
            # Validate video
            if not self._validate_video(video_path):
                raise ValueError(f"Invalid video: {video_path}")

            # Open video
            video = cv2.VideoCapture(video_path)

            if not video.isOpened():
                raise ValueError(f"Could not open video: {video_path}")

            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            frame_interval = int(fps * interval_seconds)

            logger.info("video_properties",
                       fps=fps,
                       total_frames=total_frames,
                       duration=duration)

            # Create output directory
            if output_dir is None:
                temp_dir = Path(tempfile.mkdtemp(prefix="devmind_frames_"))
            else:
                temp_dir = Path(output_dir)
                temp_dir.mkdir(parents=True, exist_ok=True)

            frames = []
            frame_count = 0
            extracted = 0

            while video.isOpened() and extracted < max_frames:
                ret, frame = video.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    frame_path = temp_dir / f"frame_{extracted:04d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frames.append(str(frame_path))
                    extracted += 1
                    logger.debug("frame_extracted",
                               frame_number=frame_count,
                               extracted_count=extracted)

                frame_count += 1

            video.release()

            logger.info("frames_extracted",
                       total_extracted=len(frames),
                       output_dir=str(temp_dir))

            return frames

        except Exception as e:
            logger.error("frame_extraction_failed",
                        error=str(e),
                        video=video_path)
            return []

    async def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract audio track from video

        Args:
            video_path: Path to video file
            output_path: Path for output audio file (default: temp file)

        Returns:
            Path to extracted audio file
        """
        logger.info("extracting_audio", video=video_path)

        try:
            # Validate video
            if not self._validate_video(video_path):
                raise ValueError(f"Invalid video: {video_path}")

            # Import moviepy (optional dependency)
            try:
                import moviepy.editor as mp
            except ImportError:
                logger.error("moviepy_not_installed")
                raise ImportError(
                    "moviepy is required for audio extraction. "
                    "Install with: pip install moviepy"
                )

            # Load video
            video = mp.VideoFileClip(video_path)

            # Generate output path if not provided
            if output_path is None:
                output_path = tempfile.mktemp(
                    suffix=".wav",
                    prefix="devmind_audio_"
                )

            # Extract audio
            if video.audio is not None:
                video.audio.write_audiofile(output_path, logger=None)
                logger.info("audio_extracted", output_path=output_path)
            else:
                logger.warning("video_has_no_audio", video=video_path)
                raise ValueError("Video has no audio track")

            video.close()

            return output_path

        except Exception as e:
            logger.error("audio_extraction_failed",
                        error=str(e),
                        video=video_path)
            raise

    async def process_meeting_video(
        self,
        video_path: str,
        language: str = "en",
        extract_action_items: bool = True
    ) -> Dict[str, Any]:
        """
        Process E3 meeting recording

        Extracts:
        - Full transcription with timestamps
        - Key visual moments from video
        - Action items and decisions
        - Meeting summary

        Args:
            video_path: Path to meeting recording
            language: Meeting language
            extract_action_items: Whether to extract action items

        Returns:
            Dict containing comprehensive meeting analysis
        """
        logger.info("processing_meeting_video",
                   video=video_path,
                   language=language)

        try:
            # Validate video
            if not self._validate_video(video_path):
                raise ValueError(f"Invalid video: {video_path}")

            # Step 1: Extract audio and transcribe
            logger.info("step_1_extracting_audio")
            audio_path = await self.extract_audio(video_path)

            logger.info("step_2_transcribing_meeting")
            transcript = await self.voice.transcribe_meeting(
                audio_path,
                language=language,
                extract_action_items=extract_action_items
            )

            # Step 2: Extract and analyze key frames
            logger.info("step_3_extracting_frames")
            frames = self.extract_frames(
                video_path,
                interval_seconds=60,
                max_frames=10
            )

            logger.info("step_4_analyzing_frames", frame_count=len(frames))
            frame_analyses = []

            for i, frame in enumerate(frames):
                logger.debug("analyzing_frame", frame_number=i+1)
                analysis = await self.vision.analyze_screenshot(frame)
                frame_analyses.append({
                    "frame_path": frame,
                    "frame_number": i,
                    "analysis": analysis
                })

            # Step 3: Generate meeting summary
            logger.info("step_5_generating_summary")
            meeting_summary = await self._generate_meeting_summary(
                transcript,
                frame_analyses
            )

            result = {
                "transcript": transcript,
                "key_moments": frame_analyses,
                "summary": meeting_summary,
                "type": "meeting",
                "video_path": video_path,
                "metadata": {
                    "language": language,
                    "frame_count": len(frames),
                    "processed_at": datetime.utcnow().isoformat()
                },
                "status": "success"
            }

            logger.info("meeting_video_processed",
                       frame_count=len(frames),
                       has_transcript=bool(transcript),
                       has_summary=bool(meeting_summary))

            return result

        except Exception as e:
            logger.error("meeting_video_processing_failed",
                        error=str(e),
                        video=video_path)
            return {
                "transcript": None,
                "key_moments": [],
                "summary": None,
                "type": "meeting",
                "video_path": video_path,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def process_demo_video(
        self,
        video_path: str,
        analyze_ui: bool = True
    ) -> Dict[str, Any]:
        """
        Process product demo video

        Args:
            video_path: Path to demo video
            analyze_ui: Whether to analyze UI in frames

        Returns:
            Dict containing demo analysis
        """
        logger.info("processing_demo_video", video=video_path)

        try:
            # Extract frames at higher frequency for demos
            frames = self.extract_frames(
                video_path,
                interval_seconds=15,
                max_frames=30
            )

            # Extract and transcribe audio
            audio_path = await self.extract_audio(video_path)
            transcript = await self.voice.process_voice_input(audio_path)

            # Analyze frames
            frame_analyses = []

            for i, frame in enumerate(frames):
                if analyze_ui:
                    analysis = await self.vision.review_ui_design(frame)
                else:
                    analysis = await self.vision.analyze_screenshot(frame)

                frame_analyses.append({
                    "frame_path": frame,
                    "frame_number": i,
                    "analysis": analysis
                })

            return {
                "transcript": transcript,
                "frames": frame_analyses,
                "type": "demo",
                "video_path": video_path,
                "metadata": {
                    "frame_count": len(frames),
                    "processed_at": datetime.utcnow().isoformat()
                },
                "status": "success"
            }

        except Exception as e:
            logger.error("demo_video_processing_failed",
                        error=str(e),
                        video=video_path)
            return {
                "transcript": None,
                "frames": [],
                "type": "demo",
                "video_path": video_path,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def _generate_meeting_summary(
        self,
        transcript: Dict[str, Any],
        frame_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive meeting summary

        Args:
            transcript: Meeting transcript data
            frame_analyses: Analyzed key frames

        Returns:
            Dict containing meeting summary
        """
        logger.info("generating_meeting_summary")

        try:
            # Combine transcript and visual insights
            transcript_text = transcript.get("transcript", "")

            # Extract key visual insights
            visual_insights = [
                f"Frame {fa['frame_number']}: {fa['analysis'].get('analysis', '')}"
                for fa in frame_analyses
                if fa.get('analysis', {}).get('status') == 'success'
            ]

            # In production, would use LLM to generate comprehensive summary
            summary = {
                "duration": transcript.get("metadata", {}).get("duration"),
                "transcript_available": bool(transcript_text),
                "key_frames_analyzed": len(frame_analyses),
                "visual_insights": visual_insights[:5],  # Top 5 insights
                "action_items": transcript.get("action_items", []),
                "generated_at": datetime.utcnow().isoformat()
            }

            return summary

        except Exception as e:
            logger.error("meeting_summary_generation_failed", error=str(e))
            return {"error": str(e)}

    async def extract_key_moments(
        self,
        video_path: str,
        moment_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract key moments from video

        Args:
            video_path: Path to video file
            moment_types: Types of moments to extract (e.g., "decision", "demo", "discussion")

        Returns:
            List of key moments with timestamps
        """
        logger.info("extracting_key_moments", video=video_path)

        try:
            # Extract frames at high frequency
            frames = self.extract_frames(
                video_path,
                interval_seconds=10,
                max_frames=50
            )

            # Analyze each frame
            key_moments = []

            for i, frame in enumerate(frames):
                analysis = await self.vision.analyze_screenshot(frame)

                if analysis.get("status") == "success":
                    # Determine if this is a key moment
                    # In production, would use more sophisticated detection
                    key_moments.append({
                        "timestamp": i * 10,  # seconds
                        "frame_path": frame,
                        "analysis": analysis,
                        "type": "visual_change"
                    })

            logger.info("key_moments_extracted", count=len(key_moments))

            return key_moments

        except Exception as e:
            logger.error("key_moment_extraction_failed", error=str(e))
            return []
