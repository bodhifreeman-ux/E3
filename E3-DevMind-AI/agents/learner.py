"""
Agent #27: LEARNER (Continuous Improvement)

Learns and improves from every interaction through feedback integration.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class LearnerAgent(BaseAgent):
    """LEARNER - Continuous Improvement Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="learner",
            agent_name="Learner",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.feedback_history: List[Dict[str, Any]] = []
        self.improvement_metrics: Dict[str, Any] = {
            "accuracy_trend": [],
            "feedback_count": 0,
            "improvements_made": 0
        }

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "continuous_improvement",
            "agent_id": "learner",
            "agent_name": "Learner",
            "tier": 5,
            "capabilities": [
                "feedback_integration",
                "accuracy_improvement",
                "error_analysis",
                "performance_tracking",
                "adaptive_learning"
            ],
            "specialization": "self_improvement"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process learning and improvement request"""
        query_type = message.content.get("query_type", "learn")

        if query_type == "learn":
            result = await self._learn_from_feedback(message.content)
        elif query_type == "analyze_errors":
            result = await self._analyze_errors(message.content)
        elif query_type == "track_performance":
            result = await self._track_performance(message.content)
        else:
            result = await self._adapt_behavior(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _learn_from_feedback(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from user feedback"""
        feedback = query_csdl.get("feedback", {})
        interaction = query_csdl.get("interaction", {})

        # Record feedback
        feedback_record = {
            "feedback": feedback,
            "interaction": interaction,
            "timestamp": "now"
        }
        self.feedback_history.append(feedback_record)
        self.improvement_metrics["feedback_count"] += 1

        # Analyze feedback for learning
        learning_query = {
            "semantic_type": "feedback_learning",
            "task": "feedback_integration",
            "feedback": feedback,
            "interaction": interaction,
            "learning_objectives": [
                "identify_error_patterns",
                "understand_user_expectations",
                "extract_improvement_opportunities",
                "update_knowledge"
            ]
        }

        learning = await self._call_vllm(learning_query, temperature=0.3)

        # Apply improvements
        if learning.get("actionable_improvements"):
            self.improvement_metrics["improvements_made"] += len(
                learning["actionable_improvements"]
            )

        return {
            "semantic_type": "learning_result",
            "learning": learning,
            "feedback_processed": True,
            "improvements_identified": len(learning.get("actionable_improvements", []))
        }

    async def _analyze_errors(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze errors and failure patterns"""
        errors = query_csdl.get("errors", [])

        error_analysis_query = {
            "semantic_type": "error_analysis",
            "task": "error_pattern_analysis",
            "errors": errors,
            "analysis_dimensions": [
                "error_categories",
                "root_causes",
                "frequency_patterns",
                "impact_assessment",
                "prevention_strategies"
            ]
        }

        analysis = await self._call_vllm(error_analysis_query, temperature=0.2)

        return {
            "semantic_type": "error_analysis_result",
            "analysis": analysis,
            "error_count": len(errors),
            "patterns_identified": analysis.get("pattern_count", 0)
        }

    async def _track_performance(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Track performance metrics over time"""
        metric_type = query_csdl.get("metric_type", "accuracy")
        timeframe = query_csdl.get("timeframe", "all")

        # Calculate metrics
        if metric_type == "accuracy":
            recent_feedback = self.feedback_history[-100:] if timeframe == "recent" else self.feedback_history

            # Analyze accuracy trend
            accuracy_query = {
                "semantic_type": "accuracy_tracking",
                "task": "accuracy_analysis",
                "feedback_history": recent_feedback,
                "analysis_type": [
                    "trend_analysis",
                    "improvement_rate",
                    "confidence_calibration"
                ]
            }

            accuracy_analysis = await self._call_vllm(accuracy_query, temperature=0.1)

            return {
                "semantic_type": "performance_result",
                "metric_type": "accuracy",
                "analysis": accuracy_analysis,
                "data_points": len(recent_feedback)
            }

        return {
            "semantic_type": "performance_result",
            "metric_type": metric_type,
            "metrics": self.improvement_metrics
        }

    async def _adapt_behavior(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt behavior based on learned patterns"""
        context = query_csdl.get("context", {})
        goal = query_csdl.get("goal", "improve_responses")

        # Analyze historical patterns
        adaptation_query = {
            "semantic_type": "behavioral_adaptation",
            "task": "behavior_optimization",
            "context": context,
            "goal": goal,
            "feedback_history": self.feedback_history[-50:],  # Recent feedback
            "adaptation_strategies": [
                "response_style_adjustment",
                "confidence_calibration",
                "detail_level_tuning",
                "error_prevention"
            ]
        }

        adaptation = await self._call_vllm(adaptation_query, temperature=0.3)

        return {
            "semantic_type": "adaptation_result",
            "goal": goal,
            "adaptation": adaptation,
            "based_on_feedback_count": len(self.feedback_history)
        }
