"""
Embedding Generator

Generates embeddings for documents and queries using various embedding models.
Supports OpenAI, HuggingFace, and custom embedding models.
"""

from typing import List, Dict, Any, Optional
import structlog
from openai import AsyncOpenAI
import asyncio

logger = structlog.get_logger()


class EmbeddingGenerator:
    """
    Generate embeddings for E3 knowledge base

    Supports multiple embedding backends:
    - OpenAI text-embedding-3-large/small
    - HuggingFace models (sentence-transformers)
    - Custom models
    """

    def __init__(
        self,
        provider: str = "openai",
        model: str = "text-embedding-3-large",
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None
    ):
        """
        Initialize Embedding Generator

        Args:
            provider: Embedding provider (openai, huggingface, custom)
            model: Model name
            api_key: API key (for OpenAI)
            dimensions: Optional dimension reduction for OpenAI models
        """
        self.provider = provider.lower()
        self.model = model
        self.dimensions = dimensions

        if self.provider == "openai":
            if not api_key:
                raise ValueError("OpenAI API key required for OpenAI embeddings")
            self.client = AsyncOpenAI(api_key=api_key)

            # Set default dimensions based on model
            if self.dimensions is None:
                if "large" in model:
                    self.dimensions = 3072
                elif "small" in model:
                    self.dimensions = 1536
                else:
                    self.dimensions = 1536

        elif self.provider == "huggingface":
            self._initialize_huggingface(model)

        logger.info("embedding_generator_initialized",
                   provider=self.provider,
                   model=self.model,
                   dimensions=self.dimensions)

    def _initialize_huggingface(self, model: str):
        """Initialize HuggingFace model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.hf_model = SentenceTransformer(model)
            self.dimensions = self.hf_model.get_sentence_embedding_dimension()
            logger.info("huggingface_model_loaded",
                       model=model,
                       dimensions=self.dimensions)
        except ImportError:
            raise ImportError(
                "sentence-transformers required for HuggingFace embeddings. "
                "Install with: pip install sentence-transformers"
            )

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.provider == "openai":
            return await self._generate_openai_embedding(text)
        elif self.provider == "huggingface":
            return await self._generate_huggingface_embedding(text)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        logger.info("generating_embeddings", count=len(texts))

        if self.provider == "openai":
            embeddings = await self._generate_openai_embeddings_batch(
                texts,
                batch_size
            )
        elif self.provider == "huggingface":
            embeddings = await self._generate_huggingface_embeddings_batch(
                texts,
                batch_size
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        logger.info("embeddings_generated", count=len(embeddings))
        return embeddings

    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error("openai_embedding_failed", error=str(e))
            raise

    async def _generate_openai_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """Generate embeddings in batches using OpenAI"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.debug("batch_processed",
                           batch_num=i // batch_size + 1,
                           batch_size=len(batch))

            except Exception as e:
                logger.error("batch_embedding_failed", error=str(e))
                # Return zero vectors for failed batch
                all_embeddings.extend([[0.0] * self.dimensions] * len(batch))

        return all_embeddings

    async def _generate_huggingface_embedding(self, text: str) -> List[float]:
        """Generate embedding using HuggingFace"""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self.hf_model.encode,
                text
            )
            return embedding.tolist()

        except Exception as e:
            logger.error("huggingface_embedding_failed", error=str(e))
            raise

    async def _generate_huggingface_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """Generate embeddings in batches using HuggingFace"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    None,
                    self.hf_model.encode,
                    batch
                )

                all_embeddings.extend([emb.tolist() for emb in embeddings])

                logger.debug("batch_processed",
                           batch_num=i // batch_size + 1,
                           batch_size=len(batch))

            except Exception as e:
                logger.error("batch_embedding_failed", error=str(e))
                # Return zero vectors for failed batch
                all_embeddings.extend([[0.0] * self.dimensions] * len(batch))

        return all_embeddings

    async def generate_document_embedding(
        self,
        document: Dict[str, Any],
        text_field: str = "content"
    ) -> List[float]:
        """
        Generate embedding for a document

        Args:
            document: Document dict
            text_field: Field containing text to embed

        Returns:
            Embedding vector
        """
        text = document.get(text_field, "")

        if not text:
            # Combine multiple fields if no main text field
            text_parts = []
            for key, value in document.items():
                if isinstance(value, str) and len(value) > 0:
                    text_parts.append(f"{key}: {value}")
            text = " | ".join(text_parts)

        return await self.generate_embedding(text)

    async def generate_document_embeddings(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "content",
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple documents

        Args:
            documents: List of documents
            text_field: Field containing text to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        # Extract texts from documents
        texts = []
        for doc in documents:
            text = doc.get(text_field, "")
            if not text:
                # Combine multiple fields
                text_parts = []
                for key, value in doc.items():
                    if isinstance(value, str) and len(value) > 0:
                        text_parts.append(f"{key}: {value}")
                text = " | ".join(text_parts) if text_parts else "empty"
            texts.append(text)

        return await self.generate_embeddings(texts, batch_size)

    def get_dimensions(self) -> int:
        """
        Get embedding dimensions

        Returns:
            Number of dimensions
        """
        return self.dimensions

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get embedding provider information

        Returns:
            Dict containing provider details
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "dimensions": self.dimensions
        }
