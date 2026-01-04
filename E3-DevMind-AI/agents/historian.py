"""
Agent #10: HISTORIAN (Institutional Memory)

E3's complete memory and context provider - remembers all decisions and outcomes.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

logger = structlog.get_logger()


class HistorianAgent(BaseAgent):
    """
    HISTORIAN - Institutional Memory Agent

    Capabilities:
    - Remembers all past E3 decisions
    - Tracks decision evolution
    - Prevents repeating mistakes
    - Provides historical context
    - Outcome tracking
    - Lesson learning
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        self.decision_archive: List[Dict[str, Any]] = []
        self.outcome_tracking: Dict[str, Any] = {}

        super().__init__(
            agent_id="historian",
            agent_name="Historian",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "institutional_memory",
            "agent_id": "historian",
            "agent_name": "Historian",
            "tier": 3,
            "capabilities": [
                "decision_tracking",
                "outcome_recording",
                "context_provision",
                "lesson_learning",
                "pattern_recognition_over_time",
                "mistake_prevention"
            ],
            "specialization": "organizational_memory",
            "perspective": "historical_context"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Provide historical context and institutional memory"""

        query_type = message.content.get("query_type", "historical_context")

        logger.info(
            "historian_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "historical_context":
            result = await self._provide_context(message.content)
        elif query_type == "decision_history":
            result = await self._retrieve_decision_history(message.content)
        elif query_type == "lessons_learned":
            result = await self._extract_lessons(message.content)
        elif query_type == "outcome_tracking":
            result = await self._track_outcomes(message.content)
        elif query_type == "record_decision":
            result = await self._record_decision(message.content)
        else:
            result = await self._general_historical_query(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _provide_context(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide historical context for current situation
        """

        query = query_csdl.get("query", "")

        # Search historical records in knowledge base
        history = await self.retrieve_knowledge(
            {"topic": query, "include_history": True, "type": "decision"},
            limit=20
        )

        context_query = {
            "semantic_type": "historical_context",
            "task": "historical_context_provision",
            "query": query,
            "historical_data": history,
            "provide": [
                "relevant_decisions",
                "outcomes",
                "lessons_learned",
                "similar_situations",
                "evolution_timeline"
            ]
        }

        context_data = await self._call_vllm(context_query, temperature=0.2)

        return {
            "semantic_type": "historical_context_result",
            "historical_context": context_data.get("context", ""),
            "relevant_decisions": context_data.get("decisions", []),
            "outcomes": context_data.get("outcomes", []),
            "lessons_learned": context_data.get("lessons", []),
            "similar_situations": context_data.get("similar", []),
            "evolution_timeline": context_data.get("timeline", []),
            "recommendations": context_data.get("recommendations", [])
        }

    async def _retrieve_decision_history(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve decision history for a topic/project
        """

        topic = query_csdl.get("topic", "")

        history_query = {
            "semantic_type": "decision_history",
            "task": "decision_history_retrieval",
            "topic": topic,
            "timeframe": query_csdl.get("timeframe", "all"),
            "retrieve": [
                "decisions_made",
                "decision_makers",
                "rationale",
                "outcomes",
                "impact"
            ]
        }

        # Get from knowledge base
        decisions = await self.retrieve_knowledge(
            {"topic": topic, "type": "decision"},
            limit=30
        )

        # Analyze with vLLM
        analysis = await self._call_vllm({
            **history_query,
            "decisions": decisions
        }, temperature=0.2)

        return {
            "semantic_type": "decision_history_result",
            "decisions": analysis.get("decisions", []),
            "timeline": analysis.get("timeline", []),
            "key_decision_points": analysis.get("key_points", []),
            "decision_evolution": analysis.get("evolution", ""),
            "impact_assessment": analysis.get("impact", {})
        }

    async def _extract_lessons(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract lessons learned from past experiences
        """

        domain = query_csdl.get("domain", "")

        lessons_query = {
            "semantic_type": "lessons_learned",
            "task": "lesson_extraction",
            "domain": domain,
            "extract": [
                "successes_and_why",
                "failures_and_why",
                "patterns_identified",
                "best_practices",
                "pitfalls_to_avoid"
            ]
        }

        # Get historical data
        historical_data = await self.retrieve_knowledge(
            {"domain": domain, "include_outcomes": True},
            limit=25
        )

        lessons = await self._call_vllm({
            **lessons_query,
            "historical_data": historical_data
        }, temperature=0.3)

        return {
            "semantic_type": "lessons_learned_result",
            "successes": lessons.get("successes", []),
            "failures": lessons.get("failures", []),
            "patterns": lessons.get("patterns", []),
            "best_practices": lessons.get("best_practices", []),
            "pitfalls": lessons.get("pitfalls", []),
            "recommendations": lessons.get("recommendations", [])
        }

    async def _track_outcomes(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track outcomes of past decisions
        """

        decision_id = query_csdl.get("decision_id", "")

        outcome_query = {
            "semantic_type": "outcome_tracking",
            "task": "outcome_tracking",
            "decision_id": decision_id,
            "track": [
                "actual_vs_expected",
                "success_metrics",
                "unexpected_consequences",
                "long_term_impact"
            ]
        }

        outcome = await self._call_vllm(outcome_query, temperature=0.2)

        # Store in tracking
        if decision_id:
            self.outcome_tracking[decision_id] = outcome

        return {
            "semantic_type": "outcome_tracking_result",
            "outcome": outcome,
            "success_level": outcome.get("success", 0.0),
            "lessons": outcome.get("lessons", [])
        }

    async def _record_decision(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Record a decision for future reference
        """

        decision = query_csdl.get("decision", {})

        record = {
            "decision_id": decision.get("id", f"decision_{datetime.now().timestamp()}"),
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": query_csdl.get("context", {}),
            "decision_makers": decision.get("makers", []),
            "rationale": decision.get("rationale", ""),
            "expected_outcome": decision.get("expected_outcome", "")
        }

        self.decision_archive.append(record)

        # Keep last 1000 decisions
        if len(self.decision_archive) > 1000:
            self.decision_archive = self.decision_archive[-1000:]

        return {
            "semantic_type": "decision_recorded",
            "status": "recorded",
            "decision_id": record["decision_id"],
            "message": "Decision recorded in institutional memory"
        }

    async def _general_historical_query(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General historical query"""

        historical_query = {
            "semantic_type": "general_historical_query",
            "task": "historical_information_retrieval",
            "query": query_csdl
        }

        # Search knowledge base
        historical_data = await self.retrieve_knowledge(query_csdl, limit=15)

        result = await self._call_vllm({
            **historical_query,
            "historical_data": historical_data
        }, temperature=0.2)

        return result
