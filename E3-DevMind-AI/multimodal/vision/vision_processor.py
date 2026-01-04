"""
Vision Intelligence Module

Handles all image/visual analysis for E3 DevMind AI.
Provides screenshot analysis, diagram understanding, whiteboard OCR, and more.
"""

from openai import AsyncOpenAI
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()


class VisionProcessor:
    """
    Vision processing for E3 DevMind AI

    Capabilities:
    - Screenshot analysis
    - Diagram understanding
    - Whiteboard OCR
    - UI/UX review
    - Code extraction from images
    - Architecture diagram analysis
    - Design mockup review
    """

    def __init__(self, openai_api_key: str, anlt_client):
        """
        Initialize Vision Processor

        Args:
            openai_api_key: OpenAI API key for GPT-4 Vision
            anlt_client: ANLT client for CSDL translation
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.anlt = anlt_client

        self.supported_formats = [
            ".png", ".jpg", ".jpeg", ".gif", ".webp"
        ]

        self.image_types = {
            "screenshot": "Analyze this screenshot. Focus on UI, errors, and code visible.",
            "diagram": "Analyze this technical diagram. Extract architecture and data flow.",
            "whiteboard": "Extract all content from this whiteboard image.",
            "code": "Extract and analyze code from this image.",
            "ui_mockup": "Review this UI/UX design mockup. Focus on usability and design patterns.",
            "architecture": "Analyze this architecture diagram. Identify components and relationships.",
            "flowchart": "Analyze this flowchart. Extract logic and decision points.",
            "error": "Analyze this error screenshot. Identify the error and suggest fixes."
        }

        logger.info("vision_processor_initialized",
                   supported_formats=len(self.supported_formats),
                   image_types=len(self.image_types))

    def _encode_image(self, image_path: str) -> str:
        """
        Encode image to base64

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _validate_image(self, image_path: str) -> bool:
        """
        Validate image file

        Args:
            image_path: Path to image file

        Returns:
            True if valid, False otherwise
        """
        path = Path(image_path)

        if not path.exists():
            logger.error("image_not_found", path=image_path)
            return False

        if path.suffix.lower() not in self.supported_formats:
            logger.error("unsupported_image_format",
                        path=image_path,
                        format=path.suffix)
            return False

        return True

    async def analyze_image(
        self,
        image_path: str,
        query: str,
        image_type: str = "general",
        detail_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Analyze image with GPT-4 Vision

        Flow: Image → GPT-4V → Analysis → ANLT → CSDL

        Args:
            image_path: Path to image file
            query: Analysis query/question
            image_type: Type of image (screenshot, diagram, whiteboard, etc.)
            detail_level: Detail level for analysis (low/high)

        Returns:
            Dict containing analysis, CSDL, and metadata
        """
        logger.info("analyzing_image",
                   file=image_path,
                   image_type=image_type)

        try:
            # Validate image
            if not self._validate_image(image_path):
                raise ValueError(f"Invalid image: {image_path}")

            # Encode image
            base64_image = self._encode_image(image_path)

            # Get system prompt for image type
            system_prompt = self.image_types.get(
                image_type,
                "Analyze this image thoroughly."
            )

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": detail_level
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2048,
                temperature=0.2
            )

            analysis_text = response.choices[0].message.content

            # Convert to CSDL via ANLT
            csdl = await self.anlt.text_to_csdl(analysis_text)

            # Extract metadata
            image_path_obj = Path(image_path)
            metadata = {
                "image_type": image_type,
                "file_path": image_path,
                "file_size": image_path_obj.stat().st_size,
                "file_format": image_path_obj.suffix,
                "detail_level": detail_level,
                "tokens_used": response.usage.total_tokens,
                "analyzed_at": datetime.utcnow().isoformat()
            }

            logger.info("image_analyzed",
                       tokens_used=metadata['tokens_used'],
                       analysis_length=len(analysis_text))

            return {
                "analysis": analysis_text,
                "csdl": csdl,
                "metadata": metadata,
                "status": "success"
            }

        except Exception as e:
            logger.error("image_analysis_failed",
                        error=str(e),
                        file=image_path)
            return {
                "analysis": None,
                "csdl": None,
                "metadata": {"error": str(e)},
                "status": "error"
            }

    async def analyze_screenshot(
        self,
        screenshot_path: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive screenshot analysis

        Args:
            screenshot_path: Path to screenshot
            focus_areas: Specific areas to focus on

        Returns:
            Dict containing detailed screenshot analysis
        """
        logger.info("analyzing_screenshot", path=screenshot_path)

        default_focus = [
            "What's shown?",
            "Any errors or warnings?",
            "Any code visible?",
            "Performance or security concerns?",
            "UI/UX observations?",
            "Recommendations?"
        ]

        focus = focus_areas or default_focus
        query = "Analyze this screenshot:\n" + "\n".join(f"{i+1}. {f}" for i, f in enumerate(focus))

        return await self.analyze_image(screenshot_path, query, "screenshot")

    async def extract_whiteboard(
        self,
        whiteboard_path: str
    ) -> Dict[str, Any]:
        """
        Extract content from whiteboard photos

        Args:
            whiteboard_path: Path to whiteboard image

        Returns:
            Dict containing extracted whiteboard content
        """
        logger.info("extracting_whiteboard", path=whiteboard_path)

        query = """Extract all content from this whiteboard:
        1. Transcribe all text accurately
        2. Describe all diagrams and drawings
        3. Organize content hierarchically
        4. Identify key points and action items
        5. Note any unclear or illegible sections"""

        return await self.analyze_image(whiteboard_path, query, "whiteboard")

    async def analyze_architecture_diagram(
        self,
        diagram_path: str
    ) -> Dict[str, Any]:
        """
        Analyze architecture diagram

        Args:
            diagram_path: Path to architecture diagram

        Returns:
            Dict containing architecture analysis
        """
        logger.info("analyzing_architecture_diagram", path=diagram_path)

        query = """Analyze this architecture diagram:
        1. Identify all components and services
        2. Map data flow and connections
        3. Identify communication patterns
        4. Note scalability considerations
        5. Identify potential bottlenecks
        6. Suggest improvements"""

        return await self.analyze_image(diagram_path, query, "architecture")

    async def extract_code_from_image(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        Extract code from image

        Args:
            image_path: Path to image containing code

        Returns:
            Dict containing extracted code
        """
        logger.info("extracting_code", path=image_path)

        query = """Extract code from this image:
        1. Transcribe all code exactly as shown
        2. Identify the programming language
        3. Format code properly with indentation
        4. Note any syntax errors visible
        5. Provide brief code explanation"""

        result = await self.analyze_image(image_path, query, "code")

        # Attempt to parse code from analysis
        if result["status"] == "success":
            code_blocks = self._extract_code_blocks(result["analysis"])
            result["code_blocks"] = code_blocks

        return result

    def _extract_code_blocks(self, analysis_text: str) -> List[Dict[str, Any]]:
        """
        Extract code blocks from analysis text

        Args:
            analysis_text: Analysis text containing code

        Returns:
            List of code blocks with language and content
        """
        code_blocks = []

        # Simple code block extraction
        # In production, would use more sophisticated parsing
        lines = analysis_text.split('\n')
        in_code_block = False
        current_block = []
        current_language = None

        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append({
                        "language": current_language,
                        "code": '\n'.join(current_block)
                    })
                    current_block = []
                    current_language = None
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    lang = line.strip()[3:].strip()
                    current_language = lang if lang else "unknown"
            elif in_code_block:
                current_block.append(line)

        return code_blocks

    async def review_ui_design(
        self,
        mockup_path: str
    ) -> Dict[str, Any]:
        """
        Review UI/UX design mockup

        Args:
            mockup_path: Path to UI mockup

        Returns:
            Dict containing UI/UX review
        """
        logger.info("reviewing_ui_design", path=mockup_path)

        query = """Review this UI/UX design mockup:
        1. Visual hierarchy and layout
        2. Color scheme and consistency
        3. Typography and readability
        4. User flow and navigation
        5. Accessibility considerations
        6. Mobile responsiveness indicators
        7. Design system compliance
        8. Improvement suggestions"""

        return await self.analyze_image(mockup_path, query, "ui_mockup")

    async def analyze_error_screenshot(
        self,
        error_screenshot_path: str
    ) -> Dict[str, Any]:
        """
        Analyze error screenshot and provide debugging help

        Args:
            error_screenshot_path: Path to error screenshot

        Returns:
            Dict containing error analysis and fixes
        """
        logger.info("analyzing_error_screenshot", path=error_screenshot_path)

        query = """Analyze this error screenshot:
        1. Identify the error type and message
        2. Determine the likely cause
        3. Identify affected code or component
        4. Suggest debugging steps
        5. Provide potential fixes
        6. Note any related errors visible"""

        return await self.analyze_image(error_screenshot_path, query, "error")

    async def batch_analyze_images(
        self,
        image_paths: List[str],
        query: str,
        image_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images in batch

        Args:
            image_paths: List of image paths
            query: Query for all images
            image_type: Type of images

        Returns:
            List of analysis results
        """
        logger.info("batch_analyzing_images",
                   count=len(image_paths),
                   image_type=image_type)

        results = []

        for image_path in image_paths:
            result = await self.analyze_image(image_path, query, image_type)
            results.append(result)

        logger.info("batch_analysis_complete",
                   total=len(results),
                   successful=sum(1 for r in results if r["status"] == "success"))

        return results
