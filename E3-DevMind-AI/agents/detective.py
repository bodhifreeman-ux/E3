"""
Agent #9: DETECTIVE (Pattern Recognition)

Discovers hidden patterns and correlations in data.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class DetectiveAgent(BaseAgent):
    """
    DETECTIVE - Pattern Recognition Agent

    Capabilities:
    - Pattern discovery in E3 data
    - Correlation analysis
    - Anomaly detection
    - Trend identification
    - Behavior analysis
    - Signal extraction from noise
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="detective",
            agent_name="Detective",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "pattern_recognition",
            "agent_id": "detective",
            "agent_name": "Detective",
            "tier": 3,
            "capabilities": [
                "pattern_discovery",
                "correlation_analysis",
                "anomaly_detection",
                "trend_identification",
                "behavior_analysis",
                "signal_extraction"
            ],
            "approach": "data_driven_investigation",
            "perspective": "patterns_and_correlations"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Discover patterns in data"""

        query_type = message.content.get("query_type", "pattern_discovery")

        logger.info(
            "detective_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "pattern_discovery":
            result = await self._discover_patterns(message.content)
        elif query_type == "correlation_analysis":
            result = await self._analyze_correlations(message.content)
        elif query_type == "anomaly_detection":
            result = await self._detect_anomalies(message.content)
        elif query_type == "trend_identification":
            result = await self._identify_trends(message.content)
        elif query_type == "behavior_analysis":
            result = await self._analyze_behavior(message.content)
        else:
            result = await self._general_pattern_analysis(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _discover_patterns(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Discover patterns in data
        """

        data = query_csdl.get("data", {})

        pattern_query = {
            "semantic_type": "pattern_discovery",
            "task": "pattern_recognition",
            "data": data,
            "find": [
                "recurring_patterns",
                "sequential_patterns",
                "temporal_patterns",
                "structural_patterns",
                "behavioral_patterns"
            ],
            "significance_threshold": query_csdl.get("threshold", 0.7)
        }

        patterns = await self._call_vllm(pattern_query, temperature=0.3)

        return {
            "semantic_type": "pattern_discovery_result",
            "patterns_discovered": patterns.get("patterns", []),
            "pattern_types": patterns.get("types", []),
            "frequency": patterns.get("frequency", {}),
            "significance": patterns.get("significance", {}),
            "insights": patterns.get("insights", [])
        }

    async def _analyze_correlations(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze correlations between variables
        """

        variables = query_csdl.get("variables", [])

        correlation_query = {
            "semantic_type": "correlation_analysis",
            "task": "correlation_analysis",
            "variables": variables,
            "data": query_csdl.get("data", {}),
            "find": [
                "strong_correlations",
                "causal_relationships",
                "hidden_connections",
                "inverse_correlations"
            ]
        }

        correlations = await self._call_vllm(correlation_query, temperature=0.3)

        return {
            "semantic_type": "correlation_result",
            "correlations": correlations.get("correlations", []),
            "strength": correlations.get("strength", {}),
            "causal_vs_correlation": correlations.get("causality", []),
            "insights": correlations.get("insights", []),
            "recommendations": correlations.get("recommendations", [])
        }

    async def _detect_anomalies(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect anomalies and outliers
        """

        data = query_csdl.get("data", {})

        anomaly_query = {
            "semantic_type": "anomaly_detection",
            "task": "anomaly_detection",
            "data": data,
            "baseline": query_csdl.get("baseline", {}),
            "detect": [
                "statistical_outliers",
                "behavioral_anomalies",
                "temporal_anomalies",
                "contextual_anomalies"
            ]
        }

        anomalies = await self._call_vllm(anomaly_query, temperature=0.3)

        return {
            "semantic_type": "anomaly_result",
            "anomalies_detected": anomalies.get("anomalies", []),
            "severity": anomalies.get("severity", {}),
            "potential_causes": anomalies.get("causes", []),
            "recommended_actions": anomalies.get("actions", []),
            "false_positive_likelihood": anomalies.get("false_positive", 0.0)
        }

    async def _identify_trends(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify trends in time-series data
        """

        data = query_csdl.get("time_series", {})

        trend_query = {
            "semantic_type": "trend_identification",
            "task": "trend_identification",
            "data": data,
            "timeframe": query_csdl.get("timeframe", ""),
            "identify": [
                "growth_trends",
                "decline_trends",
                "cyclical_patterns",
                "seasonality",
                "inflection_points"
            ]
        }

        trends = await self._call_vllm(trend_query, temperature=0.3)

        return {
            "semantic_type": "trend_result",
            "trends": trends.get("trends", []),
            "direction": trends.get("direction", ""),
            "strength": trends.get("strength", 0.0),
            "inflection_points": trends.get("inflection", []),
            "forecast": trends.get("forecast", {}),
            "confidence": trends.get("confidence", 0.0)
        }

    async def _analyze_behavior(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze behavioral patterns
        """

        behavior_data = query_csdl.get("behavior_data", {})

        behavior_query = {
            "semantic_type": "behavior_analysis",
            "task": "behavioral_pattern_analysis",
            "data": behavior_data,
            "analyze": [
                "user_behavior_patterns",
                "system_behavior_patterns",
                "interaction_patterns",
                "usage_patterns",
                "deviation_from_normal"
            ]
        }

        analysis = await self._call_vllm(behavior_query, temperature=0.3)

        return {
            "semantic_type": "behavior_analysis_result",
            "behavior_patterns": analysis.get("patterns", []),
            "typical_behaviors": analysis.get("typical", []),
            "unusual_behaviors": analysis.get("unusual", []),
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", [])
        }

    async def _general_pattern_analysis(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General pattern analysis"""

        pattern_query = {
            "semantic_type": "general_pattern_analysis",
            "task": "pattern_analysis",
            "data": query_csdl,
            "approach": "comprehensive"
        }

        result = await self._call_vllm(pattern_query, temperature=0.3)

        return result
