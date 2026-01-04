"""
Agent #2: PROPHET (Predictive Analytics)

Predicts project risks, forecasts timelines, and provides early warnings.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class ProphetAgent(BaseAgent):
    """
    PROPHET - Predictive Analytics Agent

    Capabilities:
    - Risk prediction before issues materialize
    - Timeline and deadline forecasting
    - Resource demand prediction
    - Quality trend analysis
    - Bottleneck identification
    - Early warning system
    - Scenario simulation
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        self.prediction_history: List[Dict[str, Any]] = []
        self.accuracy_tracker: Dict[str, Any] = {}

        super().__init__(
            agent_id="prophet",
            agent_name="Prophet",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "predictive_analytics",
            "agent_id": "prophet",
            "agent_name": "Prophet",
            "tier": 2,
            "capabilities": [
                "risk_prediction",
                "timeline_forecasting",
                "resource_demand_prediction",
                "quality_trend_analysis",
                "bottleneck_identification",
                "early_warning_system",
                "scenario_simulation"
            ],
            "specialization": "foresight_and_prevention",
            "outputs": "predictions_with_confidence_levels"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process predictive analytics request

        Analyzes historical data and current trends to predict future outcomes.
        """

        query_type = message.content.get("query_type", "general_prediction")

        logger.info(
            "prophet_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "risk_prediction":
            result = await self._predict_risks(message.content)
        elif query_type == "timeline_forecast":
            result = await self._forecast_timeline(message.content)
        elif query_type == "resource_demand":
            result = await self._predict_resource_demand(message.content)
        elif query_type == "quality_trends":
            result = await self._analyze_quality_trends(message.content)
        elif query_type == "bottleneck_detection":
            result = await self._identify_bottlenecks(message.content)
        else:
            result = await self._general_prediction(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id,
            metadata={
                "prediction_type": query_type,
                "confidence": result.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat()
            }
        )

    async def _predict_risks(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict potential risks in project/code/timeline

        Analyzes:
        - Historical incident patterns
        - Current project state
        - Code churn rates
        - Team velocity trends
        - External dependencies
        """

        # Retrieve relevant historical data
        historical_data = await self.retrieve_knowledge(
            {"topic": "project_risks", "timeframe": "last_6_months"},
            limit=20
        )

        # Build prediction query for CSDL-vLLM
        prediction_query = {
            "semantic_type": "prediction_request",
            "task": "risk_prediction",
            "current_state": query_csdl.get("current_state", {}),
            "historical_patterns": historical_data,
            "analysis_dimensions": [
                "timeline_risks",
                "technical_risks",
                "resource_risks",
                "quality_risks",
                "dependency_risks"
            ],
            "prediction_horizon": query_csdl.get("horizon", "30_days")
        }

        # Get prediction from vLLM
        prediction = await self._call_vllm(prediction_query, temperature=0.3)

        # Structure response
        risks = prediction.get("predicted_risks", [])

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(historical_data, risks)

        result = {
            "semantic_type": "prediction_result",
            "risks": [
                {
                    "risk_id": f"risk_{i}",
                    "description": risk.get("description"),
                    "probability": risk.get("probability", 0.0),
                    "impact": risk.get("impact", "medium"),
                    "timeframe": risk.get("timeframe", "unknown"),
                    "prevention_actions": risk.get("prevention_actions", []),
                    "indicators": risk.get("early_indicators", [])
                }
                for i, risk in enumerate(risks)
            ],
            "confidence": confidence,
            "data_quality": len(historical_data),
            "recommendation": prediction.get("recommendation", "")
        }

        # Track prediction for accuracy evaluation
        self._track_prediction(result)

        return result

    async def _forecast_timeline(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast project timeline and milestones

        Uses:
        - Historical velocity data
        - Current progress
        - Complexity estimates
        - Team capacity
        - Risk factors
        """

        # Get historical velocity
        velocity_data = await self.retrieve_knowledge(
            {"topic": "team_velocity", "metrics": "sprint_completion"},
            limit=10
        )

        forecast_query = {
            "semantic_type": "forecast_request",
            "task": "timeline_forecasting",
            "project_details": query_csdl.get("project", {}),
            "remaining_work": query_csdl.get("remaining_work", []),
            "historical_velocity": velocity_data,
            "team_capacity": query_csdl.get("team_capacity", {}),
            "constraints": query_csdl.get("constraints", [])
        }

        forecast = await self._call_vllm(forecast_query, temperature=0.2)

        return {
            "semantic_type": "forecast_result",
            "estimated_completion": forecast.get("completion_date"),
            "milestones": forecast.get("milestones", []),
            "confidence_range": forecast.get("confidence_range", {}),
            "assumptions": forecast.get("assumptions", []),
            "risk_factors": forecast.get("risk_factors", []),
            "recommendations": forecast.get("recommendations", [])
        }

    async def _predict_resource_demand(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict future resource needs

        Forecasts:
        - Compute/storage requirements
        - Team staffing needs
        - Budget requirements
        - Tool/service needs
        """

        resource_query = {
            "semantic_type": "resource_prediction",
            "task": "resource_demand_prediction",
            "current_usage": query_csdl.get("current_usage", {}),
            "growth_trajectory": query_csdl.get("growth", {}),
            "upcoming_features": query_csdl.get("roadmap", []),
            "prediction_period": query_csdl.get("period", "3_months")
        }

        prediction = await self._call_vllm(resource_query, temperature=0.3)

        return {
            "semantic_type": "resource_forecast",
            "resource_forecasts": prediction.get("forecasts", []),
            "peak_demand_periods": prediction.get("peaks", []),
            "cost_projections": prediction.get("costs", {}),
            "scaling_recommendations": prediction.get("scaling", [])
        }

    async def _analyze_quality_trends(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze quality trends and predict future quality

        Tracks:
        - Bug rates
        - Test coverage
        - Technical debt
        - Code review findings
        - Performance metrics
        """

        quality_data = await self.retrieve_knowledge(
            {"topic": "code_quality", "metrics": True},
            limit=30
        )

        trend_query = {
            "semantic_type": "trend_analysis",
            "task": "quality_trend_analysis",
            "historical_metrics": quality_data,
            "current_metrics": query_csdl.get("current_quality", {}),
            "analyze": [
                "bug_rate_trend",
                "coverage_trend",
                "debt_accumulation",
                "review_findings_trend",
                "performance_trend"
            ]
        }

        analysis = await self._call_vllm(trend_query, temperature=0.2)

        return {
            "semantic_type": "trend_analysis_result",
            "trends": analysis.get("trends", []),
            "predictions": analysis.get("predictions", []),
            "concerning_areas": analysis.get("concerns", []),
            "improvement_opportunities": analysis.get("improvements", [])
        }

    async def _identify_bottlenecks(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify current and future bottlenecks

        Analyzes:
        - Process bottlenecks
        - Technical bottlenecks
        - Resource bottlenecks
        - Team bottlenecks
        """

        bottleneck_query = {
            "semantic_type": "bottleneck_analysis",
            "task": "bottleneck_identification",
            "system_state": query_csdl.get("system", {}),
            "workflows": query_csdl.get("workflows", []),
            "metrics": query_csdl.get("metrics", {})
        }

        analysis = await self._call_vllm(bottleneck_query, temperature=0.3)

        return {
            "semantic_type": "bottleneck_result",
            "current_bottlenecks": analysis.get("current", []),
            "emerging_bottlenecks": analysis.get("emerging", []),
            "impact_assessment": analysis.get("impact", {}),
            "resolution_strategies": analysis.get("resolutions", [])
        }

    async def _general_prediction(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """General predictive analysis for any query"""

        prediction_query = {
            "semantic_type": "general_prediction",
            "task": "general_prediction",
            "query": query_csdl,
            "context": await self.retrieve_knowledge(query_csdl, limit=10)
        }

        prediction = await self._call_vllm(prediction_query, temperature=0.4)

        return prediction

    def _calculate_confidence(
        self,
        historical_data: List[Dict],
        predictions: List[Dict]
    ) -> float:
        """
        Calculate confidence level for predictions

        Based on:
        - Amount of historical data
        - Data quality
        - Pattern clarity
        - Model accuracy history
        """

        # Data quantity score
        data_score = min(len(historical_data) / 20.0, 1.0)

        # Historical accuracy score (if available)
        accuracy_score = self.accuracy_tracker.get("overall_accuracy", 0.7)

        # Pattern clarity score (from prediction details)
        clarity_score = 0.8  # Simplified

        # Weighted average
        confidence = (
            data_score * 0.3 +
            accuracy_score * 0.4 +
            clarity_score * 0.3
        )

        return round(confidence, 2)

    def _track_prediction(self, prediction: Dict[str, Any]):
        """Track prediction for later accuracy evaluation"""
        self.prediction_history.append({
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0)
        })

        # Keep last 100 predictions
        if len(self.prediction_history) > 100:
            self.prediction_history = self.prediction_history[-100:]
