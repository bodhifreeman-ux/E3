"""
Voice Intelligence Module

Handles all voice input/output for E3 DevMind AI.
Provides speech-to-text, text-to-speech, and meeting transcription capabilities.
"""

from openai import AsyncOpenAI
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog
import asyncio
from datetime import datetime

logger = structlog.get_logger()


class VoiceProcessor:
    """
    Voice processing for E3 DevMind AI

    Capabilities:
    - Speech to text using OpenAI Whisper
    - Text to speech using OpenAI TTS
    - Meeting transcription with timestamps
    - Voice command processing
    - Multi-language support
    """

    def __init__(self, openai_api_key: str, anlt_client):
        """
        Initialize Voice Processor

        Args:
            openai_api_key: OpenAI API key for Whisper and TTS
            anlt_client: ANLT client for CSDL translation
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.anlt = anlt_client
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh"
        ]
        self.voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        logger.info("voice_processor_initialized",
                   languages=len(self.supported_languages),
                   voices=len(self.voice_options))

    async def process_voice_input(
        self,
        audio_file_path: str,
        language: str = "en",
        include_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Convert voice input to CSDL

        Flow: Audio → Whisper → Text → ANLT → CSDL

        Args:
            audio_file_path: Path to audio file (mp3, mp4, wav, webm, etc.)
            language: Language code (en, es, fr, etc.)
            include_timestamps: Whether to include word-level timestamps

        Returns:
            Dict containing transcript, CSDL, and metadata
        """
        logger.info("processing_voice_input",
                   file=audio_file_path,
                   language=language)

        try:
            # Validate file exists
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Step 1: Speech to text with Whisper
            with open(audio_file_path, "rb") as audio_file:
                if include_timestamps:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"]
                    )
                else:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="json"
                    )

            transcript_text = transcript.text

            # Step 2: Text to CSDL via ANLT
            csdl = await self.anlt.text_to_csdl(transcript_text)

            # Extract metadata
            metadata = {
                "language": language,
                "file_path": audio_file_path,
                "file_size": audio_path.stat().st_size,
                "processed_at": datetime.utcnow().isoformat(),
                "duration": getattr(transcript, 'duration', None),
                "words": getattr(transcript, 'words', None),
                "segments": getattr(transcript, 'segments', None)
            }

            logger.info("voice_input_processed",
                       transcript_length=len(transcript_text),
                       duration=metadata['duration'])

            return {
                "transcript": transcript_text,
                "csdl": csdl,
                "metadata": metadata,
                "status": "success"
            }

        except Exception as e:
            logger.error("voice_input_processing_failed",
                        error=str(e),
                        file=audio_file_path)
            return {
                "transcript": None,
                "csdl": None,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def generate_voice_output(
        self,
        csdl_response: Dict[str, Any],
        voice: str = "nova",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert CSDL response to voice

        Flow: CSDL → ANLT → Text → TTS → Audio

        Args:
            csdl_response: CSDL formatted response
            voice: Voice option (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            output_path: Custom output path (default: /tmp/devmind_voice_{timestamp}.mp3)

        Returns:
            Dict containing output path and metadata
        """
        logger.info("generating_voice_output", voice=voice, speed=speed)

        try:
            # Validate voice option
            if voice not in self.voice_options:
                logger.warning("invalid_voice_option",
                             voice=voice,
                             using_default="nova")
                voice = "nova"

            # Validate speed
            speed = max(0.25, min(4.0, speed))

            # Step 1: CSDL to text via ANLT
            text = await self.anlt.csdl_to_text(csdl_response)

            # Step 2: Text to speech with OpenAI TTS
            response = await self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed
            )

            # Step 3: Save to file
            if output_path is None:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                output_path = f"/tmp/devmind_voice_{timestamp}.mp3"

            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            response.stream_to_file(output_path)

            metadata = {
                "voice": voice,
                "speed": speed,
                "text_length": len(text),
                "file_size": output_path_obj.stat().st_size,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info("voice_output_generated",
                       output_path=output_path,
                       file_size=metadata['file_size'])

            return {
                "output_path": output_path,
                "text": text,
                "metadata": metadata,
                "status": "success"
            }

        except Exception as e:
            logger.error("voice_output_generation_failed", error=str(e))
            return {
                "output_path": None,
                "text": None,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def transcribe_meeting(
        self,
        audio_file_path: str,
        language: str = "en",
        extract_action_items: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe E3 meeting with full context and analysis

        Args:
            audio_file_path: Path to meeting recording
            language: Meeting language
            extract_action_items: Whether to extract action items and key decisions

        Returns:
            Dict containing transcript, CSDL, action items, and meeting metadata
        """
        logger.info("transcribing_meeting",
                   file=audio_file_path,
                   language=language)

        try:
            # Get transcription with timestamps
            result = await self.process_voice_input(
                audio_file_path,
                language=language,
                include_timestamps=True
            )

            if result["status"] != "success":
                return result

            meeting_data = {
                "transcript": result["transcript"],
                "csdl": result["csdl"],
                "metadata": result["metadata"],
                "type": "meeting"
            }

            # Extract action items if requested
            if extract_action_items and result["transcript"]:
                action_items = await self._extract_action_items(result["transcript"])
                meeting_data["action_items"] = action_items

            logger.info("meeting_transcribed",
                       duration=result["metadata"].get("duration"),
                       action_items=len(meeting_data.get("action_items", [])))

            return meeting_data

        except Exception as e:
            logger.error("meeting_transcription_failed", error=str(e))
            return {
                "transcript": None,
                "csdl": None,
                "metadata": {"error": str(e)},
                "type": "meeting",
                "status": "error"
            }

    async def _extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Extract action items and key decisions from meeting transcript

        Args:
            transcript: Meeting transcript text

        Returns:
            List of action items with owners and deadlines
        """
        logger.info("extracting_action_items")

        try:
            # Use OpenAI to extract structured action items
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract action items from this meeting transcript.
                        For each action item, identify:
                        1. Action description
                        2. Owner (if mentioned)
                        3. Deadline (if mentioned)
                        4. Priority (high/medium/low)
                        5. Category (technical/business/administrative)

                        Return as JSON array."""
                    },
                    {
                        "role": "user",
                        "content": transcript
                    }
                ],
                temperature=0.2
            )

            # Parse action items (in production, would use JSON mode)
            action_items_text = response.choices[0].message.content

            # For now, return structured format
            # In production, would parse JSON properly
            return [
                {
                    "text": action_items_text,
                    "extracted_at": datetime.utcnow().isoformat()
                }
            ]

        except Exception as e:
            logger.error("action_item_extraction_failed", error=str(e))
            return []

    async def process_voice_command(
        self,
        audio_file_path: str,
        command_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process voice command for E3 DevMind AI

        Args:
            audio_file_path: Path to voice command audio
            command_context: Additional context for command interpretation

        Returns:
            Dict containing command, intent, and CSDL representation
        """
        logger.info("processing_voice_command", file=audio_file_path)

        try:
            # Transcribe command
            result = await self.process_voice_input(
                audio_file_path,
                include_timestamps=False
            )

            if result["status"] != "success":
                return result

            command_text = result["transcript"]

            # Identify intent
            intent = await self._identify_command_intent(command_text, command_context)

            return {
                "command": command_text,
                "intent": intent,
                "csdl": result["csdl"],
                "metadata": result["metadata"],
                "status": "success"
            }

        except Exception as e:
            logger.error("voice_command_processing_failed", error=str(e))
            return {
                "command": None,
                "intent": None,
                "csdl": None,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def _identify_command_intent(
        self,
        command_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify intent from voice command

        Args:
            command_text: Transcribed command text
            context: Additional context for interpretation

        Returns:
            Dict containing intent, confidence, and parameters
        """
        # Simple intent identification
        # In production, would use more sophisticated NLU

        intents = {
            "query": ["show", "what", "tell", "explain", "list"],
            "create": ["create", "make", "build", "generate", "add"],
            "update": ["update", "modify", "change", "edit", "fix"],
            "delete": ["delete", "remove", "clear"],
            "analyze": ["analyze", "review", "check", "assess"]
        }

        command_lower = command_text.lower()

        detected_intent = "unknown"
        confidence = 0.0

        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in command_lower:
                    detected_intent = intent
                    confidence = 0.8
                    break
            if confidence > 0:
                break

        return {
            "intent": detected_intent,
            "confidence": confidence,
            "command_text": command_text,
            "context": context
        }
