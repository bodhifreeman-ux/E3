"""
Agent #22: LIBRARIAN (Document Processor)

Ingests and processes all E3 documents across multiple formats.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog
import asyncio

logger = structlog.get_logger()


class LibrarianAgent(BaseAgent):
    """LIBRARIAN - Document Processor Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="librarian",
            agent_name="Librarian",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.processed_documents: List[Dict[str, Any]] = []

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "document_processing",
            "agent_id": "librarian",
            "agent_name": "Librarian",
            "tier": 5,
            "capabilities": [
                "multi_format_ingestion",
                "ocr_processing",
                "video_transcription",
                "metadata_extraction",
                "content_indexing"
            ],
            "specialization": "knowledge_ingestion"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process document ingestion request"""
        query_type = message.content.get("query_type", "process_documents")

        if query_type == "process_documents":
            result = await self._process_documents(message.content)
        elif query_type == "extract_metadata":
            result = await self._extract_metadata(message.content)
        else:
            result = await self._index_content(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _process_documents(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple documents"""
        documents = query_csdl.get("documents", [])

        results = []
        for doc in documents:
            result = await self._process_document(doc)
            results.append(result)
            self.processed_documents.append(result)

        return {
            "semantic_type": "document_processing_result",
            "processed_documents": len(results),
            "results": results,
            "total_content_indexed": sum(r.get("content_size", 0) for r in results)
        }

    async def _process_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document based on type"""
        doc_type = doc.get("type", "unknown")

        processing_query = {
            "semantic_type": "document_processing",
            "task": f"{doc_type}_processing",
            "document": doc,
            "extraction": [
                "text_content",
                "metadata",
                "structure",
                "entities"
            ]
        }

        result = await self._call_vllm(processing_query, temperature=0.2)

        return {
            "document_id": doc.get("id"),
            "type": doc_type,
            "status": "processed",
            "content": result,
            "content_size": len(str(result))
        }

    async def _extract_metadata(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from documents"""
        document = query_csdl.get("document", {})

        metadata_query = {
            "semantic_type": "metadata_extraction",
            "task": "metadata_extraction",
            "document": document,
            "fields": [
                "title",
                "author",
                "date",
                "tags",
                "categories",
                "entities"
            ]
        }

        metadata = await self._call_vllm(metadata_query, temperature=0.1)
        return {"semantic_type": "metadata_result", "metadata": metadata}

    async def _index_content(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Index content for semantic search"""
        content = query_csdl.get("content", {})

        indexing_query = {
            "semantic_type": "content_indexing",
            "task": "semantic_indexing",
            "content": content,
            "index_strategy": [
                "semantic_chunking",
                "entity_extraction",
                "relationship_mapping"
            ]
        }

        index_result = await self._call_vllm(indexing_query, temperature=0.1)
        return {"semantic_type": "indexing_result", "index": index_result}
