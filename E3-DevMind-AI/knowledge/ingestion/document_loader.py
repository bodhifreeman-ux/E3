"""
Document Ingestion Pipeline

Loads and processes documents into E3 knowledge base.
Supports multiple document types with intelligent routing to appropriate processors.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
import structlog
from datetime import datetime

logger = structlog.get_logger()


class DocumentLoader:
    """
    Load and process documents for E3 knowledge base

    Supports:
    - PDF, DOCX, TXT, MD (text documents)
    - Images (OCR via Vision Processor)
    - Videos (transcription via Video Processor)
    - Code repositories
    - Audio files (transcription via Voice Processor)
    """

    def __init__(
        self,
        librarian_agent,
        knowledge_store,
        multimodal_processor=None
    ):
        """
        Initialize Document Loader

        Args:
            librarian_agent: Librarian agent for document processing
            knowledge_store: Knowledge store for persistence
            multimodal_processor: Optional multimodal processor for images/video/audio
        """
        self.librarian = librarian_agent
        self.store = knowledge_store
        self.multimodal = multimodal_processor

        self.supported_extensions = {
            'text': {'.pdf', '.docx', '.doc', '.txt', '.md', '.rst', '.tex'},
            'image': {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'},
            'video': {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'},
            'audio': {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'},
            'code': {
                '.py', '.js', '.java', '.cpp', '.c', '.h', '.hpp',
                '.cs', '.go', '.rs', '.ts', '.jsx', '.tsx', '.rb',
                '.php', '.swift', '.kt', '.scala', '.r', '.m', '.mm'
            }
        }

        self.batch_size = 10
        self.max_concurrent = 5

        logger.info("document_loader_initialized",
                   supported_types=list(self.supported_extensions.keys()))

    async def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        file_pattern: str = "*",
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ingest all documents in a directory

        Args:
            directory_path: Path to directory
            recursive: Whether to search subdirectories
            file_pattern: Glob pattern for files (e.g., "*.pdf")
            exclude_patterns: Patterns to exclude (e.g., ["node_modules", ".git"])

        Returns:
            Dict containing ingestion statistics
        """
        logger.info("ingesting_directory",
                   path=directory_path,
                   recursive=recursive,
                   pattern=file_pattern)

        try:
            path = Path(directory_path)

            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")

            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {directory_path}")

            # Find all files
            if recursive:
                files = list(path.rglob(file_pattern))
            else:
                files = list(path.glob(file_pattern))

            # Apply exclusion patterns
            if exclude_patterns:
                files = [
                    f for f in files
                    if not any(pattern in str(f) for pattern in exclude_patterns)
                ]

            # Filter for supported formats
            all_supported = set().union(*self.supported_extensions.values())
            documents = [
                f for f in files
                if f.is_file() and f.suffix.lower() in all_supported
            ]

            logger.info("found_documents",
                       total=len(documents),
                       directory=directory_path)

            # Process in batches with concurrency control
            results = []
            semaphore = asyncio.Semaphore(self.max_concurrent)

            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]

                # Process batch with concurrency limit
                async def process_with_limit(doc):
                    async with semaphore:
                        return await self._ingest_document(doc)

                batch_results = await asyncio.gather(*[
                    process_with_limit(doc) for doc in batch
                ], return_exceptions=True)

                # Handle exceptions in results
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error("batch_processing_error", error=str(result))
                        results.append({
                            "status": "failed",
                            "error": str(result)
                        })
                    else:
                        results.append(result)

                logger.info("batch_processed",
                           batch_num=i // self.batch_size + 1,
                           batch_size=len(batch))

            # Calculate statistics
            successful = [r for r in results if r.get("status") == "success"]
            failed = [r for r in results if r.get("status") == "failed"]

            # Group by document type
            by_type = {}
            for result in successful:
                doc_type = result.get("type", "unknown")
                by_type[doc_type] = by_type.get(doc_type, 0) + 1

            summary = {
                "directory": directory_path,
                "total_documents": len(documents),
                "processed": len(successful),
                "failed": len(failed),
                "by_type": by_type,
                "ingestion_time": datetime.utcnow().isoformat(),
                "results": results
            }

            logger.info("directory_ingestion_complete",
                       total=len(documents),
                       successful=len(successful),
                       failed=len(failed))

            return summary

        except Exception as e:
            logger.error("directory_ingestion_failed",
                        error=str(e),
                        path=directory_path)
            return {
                "directory": directory_path,
                "total_documents": 0,
                "processed": 0,
                "failed": 0,
                "error": str(e),
                "status": "error"
            }

    async def ingest_document(self, document_path: str) -> Dict[str, Any]:
        """
        Ingest a single document

        Args:
            document_path: Path to document

        Returns:
            Dict containing ingestion result
        """
        return await self._ingest_document(Path(document_path))

    async def _ingest_document(self, doc_path: Path) -> Dict[str, Any]:
        """
        Internal method to ingest a single document

        Args:
            doc_path: Path object for document

        Returns:
            Dict containing ingestion result
        """
        logger.info("ingesting_document", path=str(doc_path))

        try:
            # Determine document type
            doc_type = self._get_document_type(doc_path)

            if doc_type == "unknown":
                logger.warning("unsupported_document_type",
                             path=str(doc_path),
                             extension=doc_path.suffix)
                return {
                    "document": str(doc_path),
                    "status": "failed",
                    "error": f"Unsupported document type: {doc_path.suffix}"
                }

            # Process based on type
            if doc_type in ["text", "pdf", "code"]:
                content = await self._process_text_document(doc_path, doc_type)
            elif doc_type == "image":
                content = await self._process_image_document(doc_path)
            elif doc_type == "video":
                content = await self._process_video_document(doc_path)
            elif doc_type == "audio":
                content = await self._process_audio_document(doc_path)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")

            # Store in knowledge base
            document_id = await self.store.add_document({
                "path": str(doc_path),
                "name": doc_path.name,
                "type": doc_type,
                "content": content,
                "metadata": {
                    "size": doc_path.stat().st_size,
                    "extension": doc_path.suffix,
                    "ingested_at": datetime.utcnow().isoformat()
                }
            })

            logger.info("document_ingested",
                       path=str(doc_path),
                       type=doc_type,
                       document_id=document_id)

            return {
                "document": str(doc_path),
                "document_id": document_id,
                "status": "success",
                "type": doc_type
            }

        except Exception as e:
            logger.error("document_ingestion_failed",
                        error=str(e),
                        path=str(doc_path))
            return {
                "document": str(doc_path),
                "status": "failed",
                "error": str(e)
            }

    async def _process_text_document(
        self,
        doc_path: Path,
        doc_type: str
    ) -> Dict[str, Any]:
        """
        Process text document using Librarian agent

        Args:
            doc_path: Path to document
            doc_type: Document type

        Returns:
            Processed document content
        """
        from csdl.protocol import CSDLMessage

        # Create CSDL message for Librarian
        message = CSDLMessage(
            message_type="request",
            sender_id="document_loader",
            content={
                "query_type": "process_documents",
                "documents": [{
                    "id": str(doc_path),
                    "path": str(doc_path),
                    "type": doc_type,
                    "name": doc_path.name
                }]
            }
        )

        # Process with Librarian agent
        result = await self.librarian.process_csdl(message)

        return result.content

    async def _process_image_document(self, doc_path: Path) -> Dict[str, Any]:
        """
        Process image document using Vision Processor

        Args:
            doc_path: Path to image

        Returns:
            Processed image content
        """
        if self.multimodal is None:
            raise ValueError("Multimodal processor required for image processing")

        # Use whiteboard extraction for comprehensive OCR
        result = await self.multimodal.vision.extract_whiteboard(str(doc_path))

        return {
            "analysis": result.get("analysis"),
            "csdl": result.get("csdl"),
            "metadata": result.get("metadata")
        }

    async def _process_video_document(self, doc_path: Path) -> Dict[str, Any]:
        """
        Process video document using Video Processor

        Args:
            doc_path: Path to video

        Returns:
            Processed video content
        """
        if self.multimodal is None:
            raise ValueError("Multimodal processor required for video processing")

        # Process as meeting video for comprehensive analysis
        result = await self.multimodal.video.process_meeting_video(str(doc_path))

        return {
            "transcript": result.get("transcript"),
            "key_moments": result.get("key_moments"),
            "summary": result.get("summary"),
            "metadata": result.get("metadata")
        }

    async def _process_audio_document(self, doc_path: Path) -> Dict[str, Any]:
        """
        Process audio document using Voice Processor

        Args:
            doc_path: Path to audio

        Returns:
            Processed audio content
        """
        if self.multimodal is None:
            raise ValueError("Multimodal processor required for audio processing")

        # Transcribe audio
        result = await self.multimodal.voice.transcribe_meeting(str(doc_path))

        return {
            "transcript": result.get("transcript"),
            "csdl": result.get("csdl"),
            "metadata": result.get("metadata")
        }

    def _get_document_type(self, path: Path) -> str:
        """
        Determine document type from extension

        Args:
            path: Path to document

        Returns:
            Document type string
        """
        ext = path.suffix.lower()

        for doc_type, extensions in self.supported_extensions.items():
            if ext in extensions:
                return doc_type

        return "unknown"

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get all supported file formats

        Returns:
            Dict mapping document types to supported extensions
        """
        return {
            doc_type: list(extensions)
            for doc_type, extensions in self.supported_extensions.items()
        }

    async def batch_ingest_files(
        self,
        file_paths: List[str]
    ) -> Dict[str, Any]:
        """
        Ingest a list of specific files

        Args:
            file_paths: List of file paths to ingest

        Returns:
            Dict containing batch ingestion statistics
        """
        logger.info("batch_ingesting_files", count=len(file_paths))

        # Convert to Path objects and validate
        documents = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists() and path.is_file():
                documents.append(path)
            else:
                logger.warning("file_not_found", path=file_path)

        # Process documents
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_with_limit(doc):
            async with semaphore:
                return await self._ingest_document(doc)

        results = await asyncio.gather(*[
            process_with_limit(doc) for doc in documents
        ], return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error("file_processing_error", error=str(result))
                processed_results.append({
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        successful = [r for r in processed_results if r.get("status") == "success"]
        failed = [r for r in processed_results if r.get("status") == "failed"]

        return {
            "total_files": len(file_paths),
            "processed": len(successful),
            "failed": len(failed),
            "results": processed_results
        }
