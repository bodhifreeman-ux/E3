"""
Qdrant Vector Database Manager

Manages E3's vector storage for semantic search.
Provides high-performance vector similarity search for CSDL-optimized embeddings.
"""

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, Range
)
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
import uuid

logger = structlog.get_logger()


class QdrantManager:
    """
    Qdrant vector database for E3 knowledge

    Stores CSDL-optimized embeddings for fast semantic search.
    Supports filtered search, batch operations, and collection management.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        use_https: bool = False
    ):
        """
        Initialize Qdrant Manager

        Args:
            host: Qdrant server host
            port: Qdrant server port
            api_key: Optional API key for authentication
            use_https: Whether to use HTTPS
        """
        self.host = host
        self.port = port

        # Initialize client
        if api_key:
            self.client = AsyncQdrantClient(
                host=host,
                port=port,
                api_key=api_key,
                https=use_https
            )
        else:
            self.client = AsyncQdrantClient(
                host=host,
                port=port
            )

        self.collection_name = "e3_knowledge"
        self.vector_size = 768  # Default for many embedding models

        logger.info("qdrant_manager_initialized",
                   host=host,
                   port=port,
                   collection=self.collection_name)

    async def initialize(
        self,
        vector_size: int = 768,
        distance: str = "cosine",
        recreate: bool = False
    ) -> bool:
        """
        Initialize Qdrant collection

        Args:
            vector_size: Size of embedding vectors
            distance: Distance metric (cosine, euclid, dot)
            recreate: Whether to recreate collection if it exists

        Returns:
            True if successful
        """
        logger.info("initializing_qdrant_collection",
                   vector_size=vector_size,
                   distance=distance)

        try:
            self.vector_size = vector_size

            # Map distance string to Distance enum
            distance_map = {
                "cosine": Distance.COSINE,
                "euclid": Distance.EUCLID,
                "dot": Distance.DOT
            }

            distance_metric = distance_map.get(distance.lower(), Distance.COSINE)

            # Check if collection exists
            collections = await self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)

            if exists:
                if recreate:
                    logger.warning("recreating_collection",
                                 collection=self.collection_name)
                    await self.client.delete_collection(self.collection_name)
                    exists = False
                else:
                    logger.info("collection_already_exists",
                              collection=self.collection_name)
                    return True

            if not exists:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=distance_metric
                    )
                )
                logger.info("collection_created", collection=self.collection_name)

            return True

        except Exception as e:
            logger.error("collection_initialization_failed", error=str(e))
            return False

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents with embeddings to Qdrant

        Args:
            documents: List of document payloads
            embeddings: List of embedding vectors
            batch_size: Batch size for uploads

        Returns:
            True if successful
        """
        logger.info("adding_documents_to_qdrant", count=len(documents))

        try:
            if len(documents) != len(embeddings):
                raise ValueError(
                    f"Documents ({len(documents)}) and embeddings "
                    f"({len(embeddings)}) count mismatch"
                )

            # Generate unique IDs for documents
            total_added = 0

            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]

                points = [
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            **doc,
                            "indexed_at": datetime.utcnow().isoformat()
                        }
                    )
                    for doc, embedding in zip(batch_docs, batch_embeddings)
                ]

                await self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                total_added += len(points)

                logger.debug("batch_added",
                           batch_num=i // batch_size + 1,
                           batch_size=len(points))

            logger.info("documents_added",
                       total=total_added,
                       collection=self.collection_name)

            return True

        except Exception as e:
            logger.error("document_addition_failed", error=str(e))
            return False

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in E3 knowledge

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters (e.g., {"type": "pdf", "category": "technical"})
            score_threshold: Minimum similarity score

        Returns:
            List of search results with documents and scores
        """
        logger.info("searching_qdrant",
                   limit=limit,
                   has_filters=bool(filters))

        try:
            # Build filter if provided
            query_filter = None
            if filters:
                query_filter = self._build_filter(filters)

            # Perform search
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold
            )

            search_results = [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "document": hit.payload
                }
                for hit in results
            ]

            logger.info("search_complete",
                       results_count=len(search_results),
                       limit=limit)

            return search_results

        except Exception as e:
            logger.error("search_failed", error=str(e))
            return []

    async def batch_search(
        self,
        query_embeddings: List[List[float]],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Batch semantic search

        Args:
            query_embeddings: List of query embedding vectors
            limit: Maximum results per query
            filters: Optional filters

        Returns:
            List of search results for each query
        """
        logger.info("batch_searching_qdrant", query_count=len(query_embeddings))

        try:
            # Build filter if provided
            query_filter = None
            if filters:
                query_filter = self._build_filter(filters)

            # Perform batch search
            batch_results = await self.client.search_batch(
                collection_name=self.collection_name,
                requests=[
                    {
                        "vector": embedding,
                        "limit": limit,
                        "filter": query_filter
                    }
                    for embedding in query_embeddings
                ]
            )

            # Format results
            formatted_results = []
            for results in batch_results:
                formatted_results.append([
                    {
                        "id": str(hit.id),
                        "score": hit.score,
                        "document": hit.payload
                    }
                    for hit in results
                ])

            logger.info("batch_search_complete", query_count=len(formatted_results))

            return formatted_results

        except Exception as e:
            logger.error("batch_search_failed", error=str(e))
            return [[] for _ in query_embeddings]

    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from dict

        Args:
            filters: Filter dictionary

        Returns:
            Qdrant Filter object
        """
        conditions = []

        for key, value in filters.items():
            if isinstance(value, (str, int, bool)):
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            elif isinstance(value, dict):
                # Range filter
                if "gte" in value or "lte" in value:
                    conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(
                                gte=value.get("gte"),
                                lte=value.get("lte")
                            )
                        )
                    )

        return Filter(must=conditions) if conditions else None

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection statistics

        Returns:
            Dict containing collection information
        """
        try:
            info = await self.client.get_collection(self.collection_name)

            return {
                "collection_name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "indexed": info.indexed_vectors_count,
                "status": info.status,
                "vector_size": self.vector_size
            }

        except Exception as e:
            logger.error("failed_to_get_collection_info", error=str(e))
            return {"error": str(e)}

    async def delete_by_filter(self, filters: Dict[str, Any]) -> bool:
        """
        Delete documents by filter

        Args:
            filters: Filter criteria

        Returns:
            True if successful
        """
        logger.info("deleting_by_filter", filters=filters)

        try:
            query_filter = self._build_filter(filters)

            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=query_filter
            )

            logger.info("deletion_complete")
            return True

        except Exception as e:
            logger.error("deletion_failed", error=str(e))
            return False

    async def update_payload(
        self,
        point_id: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Update document payload

        Args:
            point_id: Point ID
            payload: New payload data

        Returns:
            True if successful
        """
        try:
            await self.client.set_payload(
                collection_name=self.collection_name,
                payload=payload,
                points=[point_id]
            )

            logger.info("payload_updated", point_id=point_id)
            return True

        except Exception as e:
            logger.error("payload_update_failed", error=str(e))
            return False

    async def scroll_documents(
        self,
        limit: int = 100,
        offset: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scroll through documents

        Args:
            limit: Number of documents to return
            offset: Offset for pagination
            filters: Optional filters

        Returns:
            Dict containing documents and next offset
        """
        try:
            query_filter = None
            if filters:
                query_filter = self._build_filter(filters)

            results, next_offset = await self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
                scroll_filter=query_filter
            )

            documents = [
                {
                    "id": str(point.id),
                    "payload": point.payload
                }
                for point in results
            ]

            return {
                "documents": documents,
                "next_offset": next_offset,
                "count": len(documents)
            }

        except Exception as e:
            logger.error("scroll_failed", error=str(e))
            return {"documents": [], "next_offset": None, "count": 0}

    async def health_check(self) -> bool:
        """
        Check if Qdrant is healthy

        Returns:
            True if healthy
        """
        try:
            collections = await self.client.get_collections()
            return True
        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return False
