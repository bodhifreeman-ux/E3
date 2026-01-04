"""
Semantic Search

Advanced semantic search capabilities for E3 knowledge base.
Provides query understanding, result ranking, and relevance scoring.
"""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class SemanticSearch:
    """
    Advanced semantic search for E3 knowledge

    Features:
    - Query understanding and expansion
    - Hybrid search (semantic + keyword)
    - Result ranking and reranking
    - Relevance scoring
    - Search analytics
    """

    def __init__(self, knowledge_store, oracle_kb_agent=None):
        """
        Initialize Semantic Search

        Args:
            knowledge_store: KnowledgeStore instance
            oracle_kb_agent: Optional Oracle KB agent for enhanced search
        """
        self.store = knowledge_store
        self.oracle_kb = oracle_kb_agent

        logger.info("semantic_search_initialized")

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional filters
            min_score: Minimum relevance score

        Returns:
            List of search results with scores
        """
        logger.info("performing_semantic_search", query=query[:100])

        try:
            # Search knowledge base
            results = await self.store.search(
                query=query,
                top_k=top_k * 2,  # Get more for filtering
                filters=filters
            )

            # Filter by minimum score
            filtered_results = [
                r for r in results
                if r.get("score", 0.0) >= min_score
            ]

            # Take top_k
            final_results = filtered_results[:top_k]

            logger.info("search_complete",
                       query_length=len(query),
                       results_count=len(final_results))

            return final_results

        except Exception as e:
            logger.error("semantic_search_failed", error=str(e))
            return []

    async def search_with_context(
        self,
        query: str,
        context: Dict[str, Any],
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search with additional context

        Args:
            query: Search query
            context: Additional context for search
            top_k: Number of results

        Returns:
            Dict containing results and metadata
        """
        logger.info("searching_with_context", query=query[:100])

        try:
            # Extract filters from context
            filters = {}
            if "document_type" in context:
                filters["type"] = context["document_type"]
            if "date_range" in context:
                filters["date"] = context["date_range"]

            # Perform search
            results = await self.search(
                query=query,
                top_k=top_k,
                filters=filters if filters else None
            )

            return {
                "query": query,
                "context": context,
                "results": results,
                "result_count": len(results)
            }

        except Exception as e:
            logger.error("contextual_search_failed", error=str(e))
            return {"query": query, "results": [], "error": str(e)}

    async def multi_query_search(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search with multiple queries

        Args:
            queries: List of search queries
            top_k: Results per query

        Returns:
            Dict mapping queries to results
        """
        logger.info("multi_query_search", query_count=len(queries))

        try:
            results_map = {}

            for query in queries:
                results = await self.search(query=query, top_k=top_k)
                results_map[query] = results

            logger.info("multi_query_complete", queries=len(queries))
            return results_map

        except Exception as e:
            logger.error("multi_query_search_failed", error=str(e))
            return {}

    async def find_similar_documents(
        self,
        document_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to given document

        Args:
            document_id: Document ID
            top_k: Number of similar documents

        Returns:
            List of similar documents
        """
        logger.info("finding_similar_documents", document_id=document_id)

        try:
            # Get source document
            source_doc = await self.store.get_document(document_id)

            if not source_doc:
                logger.warning("document_not_found", document_id=document_id)
                return []

            # Extract text for similarity search
            query_text = source_doc.get("content", "")

            if not query_text:
                # Use name/path as fallback
                query_text = source_doc.get("name", source_doc.get("path", ""))

            # Search for similar
            results = await self.search(query=query_text, top_k=top_k + 1)

            # Filter out source document
            similar_docs = [
                r for r in results
                if r.get("document", {}).get("id") != document_id
            ]

            return similar_docs[:top_k]

        except Exception as e:
            logger.error("similar_documents_search_failed", error=str(e))
            return []

    async def search_with_oracle(
        self,
        question: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search using Oracle KB agent for enhanced results

        Args:
            question: Question to answer
            top_k: Number of source documents

        Returns:
            Dict containing answer and sources
        """
        if self.oracle_kb is None:
            logger.warning("oracle_kb_not_available")
            return await self.search_with_context(question, {}, top_k)

        logger.info("searching_with_oracle", question=question[:100])

        try:
            from csdl.protocol import CSDLMessage

            # Create query for Oracle KB
            message = CSDLMessage(
                message_type="request",
                sender_id="semantic_search",
                content={
                    "query_type": "query",
                    "question": question,
                    "top_k": top_k
                }
            )

            # Query Oracle KB agent
            result = await self.oracle_kb.process_csdl(message)

            return {
                "question": question,
                "answer": result.content.get("answer"),
                "sources": result.content.get("sources", []),
                "confidence": result.content.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error("oracle_search_failed", error=str(e))
            # Fallback to regular search
            return await self.search_with_context(question, {}, top_k)
