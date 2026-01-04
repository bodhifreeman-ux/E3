"""
Agent #26: ORACLE KB (Knowledge Base Query)

Instant answers from E3 knowledge base with semantic search.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class OracleKBAgent(BaseAgent):
    """ORACLE KB - Knowledge Base Query Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="oracle_kb",
            agent_name="Oracle KB",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.query_cache: Dict[str, Any] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "knowledge_retrieval",
            "agent_id": "oracle_kb",
            "agent_name": "Oracle KB",
            "tier": 5,
            "capabilities": [
                "semantic_search",
                "answer_generation",
                "citation_tracking",
                "fact_verification",
                "knowledge_retrieval"
            ],
            "specialization": "instant_knowledge_access"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process knowledge base query"""
        query_type = message.content.get("query_type", "query")

        if query_type == "query":
            result = await self._query_knowledge(message.content)
        elif query_type == "semantic_search":
            result = await self._semantic_search(message.content)
        elif query_type == "verify":
            result = await self._verify_fact(message.content)
        else:
            result = await self._retrieve_context(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _query_knowledge(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Query knowledge base and generate answer with citations"""
        question = query_csdl.get("question", "")

        # Check cache
        if question in self.query_cache:
            logger.info("kb_query_cache_hit", question=question)
            return self.query_cache[question]

        # Retrieve relevant knowledge
        kb_results = await self.knowledge_base.search(
            query=question,
            top_k=query_csdl.get("top_k", 10)
        )

        # Generate answer with vLLM
        answer_query = {
            "semantic_type": "kb_query_answer",
            "task": "answer_generation",
            "question": question,
            "retrieved_knowledge": kb_results,
            "requirements": [
                "accurate_answer",
                "cite_sources",
                "confidence_score",
                "alternative_interpretations"
            ]
        }

        answer = await self._call_vllm(answer_query, temperature=0.2)

        result = {
            "semantic_type": "kb_answer_result",
            "question": question,
            "answer": answer,
            "sources": kb_results,
            "source_count": len(kb_results)
        }

        # Cache result
        self.query_cache[question] = result

        return result

    async def _semantic_search(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search in knowledge base"""
        query = query_csdl.get("query", "")
        filters = query_csdl.get("filters", {})
        top_k = query_csdl.get("top_k", 20)

        # Perform semantic search
        results = await self.knowledge_base.search(
            query=query,
            filters=filters,
            top_k=top_k
        )

        # Rank and refine results
        ranking_query = {
            "semantic_type": "result_ranking",
            "task": "relevance_ranking",
            "query": query,
            "results": results,
            "ranking_criteria": [
                "semantic_relevance",
                "recency",
                "authority",
                "completeness"
            ]
        }

        ranked_results = await self._call_vllm(ranking_query, temperature=0.1)

        return {
            "semantic_type": "search_result",
            "query": query,
            "results": ranked_results,
            "result_count": len(results)
        }

    async def _verify_fact(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a fact against knowledge base"""
        claim = query_csdl.get("claim", "")

        # Search for supporting/contradicting evidence
        evidence = await self.knowledge_base.search(
            query=claim,
            top_k=15
        )

        verification_query = {
            "semantic_type": "fact_verification",
            "task": "claim_verification",
            "claim": claim,
            "evidence": evidence,
            "verification_criteria": [
                "supporting_evidence",
                "contradicting_evidence",
                "evidence_quality",
                "confidence_level"
            ]
        }

        verification = await self._call_vllm(verification_query, temperature=0.1)

        return {
            "semantic_type": "verification_result",
            "claim": claim,
            "verification": verification,
            "evidence_count": len(evidence),
            "verdict": verification.get("verdict", "unknown")
        }

    async def _retrieve_context(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve contextual knowledge"""
        topic = query_csdl.get("topic", "")
        depth = query_csdl.get("depth", "medium")

        # Determine top_k based on depth
        top_k_map = {"shallow": 5, "medium": 15, "deep": 30}
        top_k = top_k_map.get(depth, 15)

        # Retrieve context
        context = await self.knowledge_base.search(
            query=topic,
            top_k=top_k
        )

        # Synthesize context
        context_query = {
            "semantic_type": "context_synthesis",
            "task": "context_generation",
            "topic": topic,
            "retrieved_data": context,
            "synthesis_requirements": [
                "comprehensive_overview",
                "key_concepts",
                "relationships",
                "relevant_details"
            ]
        }

        synthesized_context = await self._call_vllm(context_query, temperature=0.2)

        return {
            "semantic_type": "context_result",
            "topic": topic,
            "context": synthesized_context,
            "depth": depth,
            "source_count": len(context)
        }
