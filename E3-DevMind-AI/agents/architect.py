"""
Agent #12: ARCHITECT (System Designer)

Technical architecture and system design expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class ArchitectAgent(BaseAgent):
    """
    ARCHITECT - System Designer Agent

    Capabilities:
    - System architecture design
    - Component design and specification
    - Integration architecture
    - Scalability design
    - Infrastructure planning
    - Technology selection
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="architect",
            agent_name="Architect",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "system_architecture",
            "agent_id": "architect",
            "agent_name": "Architect",
            "tier": 4,
            "capabilities": [
                "architecture_design",
                "component_design",
                "integration_architecture",
                "scalability_design",
                "infrastructure_planning",
                "technology_selection"
            ],
            "specialization": "technical_architecture",
            "perspective": "system_level_design"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Design system architecture"""

        query_type = message.content.get("query_type", "architecture_design")

        logger.info(
            "architect_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "architecture_design":
            result = await self._design_architecture(message.content)
        elif query_type == "component_design":
            result = await self._design_component(message.content)
        elif query_type == "integration_architecture":
            result = await self._design_integration(message.content)
        elif query_type == "scalability_design":
            result = await self._design_scalability(message.content)
        elif query_type == "technology_selection":
            result = await self._select_technologies(message.content)
        else:
            result = await self._general_design(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _design_architecture(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design complete system architecture
        """

        requirements = query_csdl.get("requirements", {})

        design_query = {
            "semantic_type": "architecture_design",
            "task": "architecture_design",
            "requirements": requirements,
            "design": [
                "system_architecture",
                "component_specs",
                "data_flow",
                "scalability_strategy",
                "technology_stack",
                "security_architecture"
            ],
            "constraints": query_csdl.get("constraints", []),
            "design_principles": [
                "separation_of_concerns",
                "modularity",
                "scalability",
                "maintainability",
                "security_by_design"
            ]
        }

        architecture = await self._call_vllm(design_query, temperature=0.3)

        return {
            "semantic_type": "architecture_design_result",
            "architecture_design": architecture.get("design", {}),
            "components": architecture.get("components", []),
            "data_flow": architecture.get("data_flow", {}),
            "technology_recommendations": architecture.get("technologies", []),
            "scalability_strategy": architecture.get("scalability", {}),
            "security_considerations": architecture.get("security", []),
            "deployment_model": architecture.get("deployment", {})
        }

    async def _design_component(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design individual component
        """

        component_spec = query_csdl.get("component", {})

        component_query = {
            "semantic_type": "component_design",
            "task": "component_design",
            "specification": component_spec,
            "design": [
                "component_interface",
                "internal_structure",
                "dependencies",
                "data_model",
                "error_handling",
                "performance_requirements"
            ]
        }

        design = await self._call_vllm(component_query, temperature=0.3)

        return {
            "semantic_type": "component_design_result",
            "component_design": design.get("design", {}),
            "interface": design.get("interface", {}),
            "internal_structure": design.get("structure", {}),
            "dependencies": design.get("dependencies", []),
            "data_model": design.get("data_model", {}),
            "implementation_notes": design.get("notes", [])
        }

    async def _design_integration(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design integration architecture
        """

        systems = query_csdl.get("systems", [])

        integration_query = {
            "semantic_type": "integration_architecture",
            "task": "integration_architecture_design",
            "systems": systems,
            "design": [
                "integration_patterns",
                "api_specifications",
                "data_synchronization",
                "error_handling",
                "monitoring"
            ]
        }

        integration = await self._call_vllm(integration_query, temperature=0.3)

        return {
            "semantic_type": "integration_design_result",
            "integration_architecture": integration.get("architecture", {}),
            "integration_patterns": integration.get("patterns", []),
            "api_specs": integration.get("apis", []),
            "data_sync_strategy": integration.get("sync", {}),
            "error_handling": integration.get("errors", {})
        }

    async def _design_scalability(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design scalability strategy
        """

        current_system = query_csdl.get("current_system", {})
        growth_projections = query_csdl.get("growth", {})

        scalability_query = {
            "semantic_type": "scalability_design",
            "task": "scalability_strategy_design",
            "current_system": current_system,
            "growth_projections": growth_projections,
            "design": [
                "horizontal_scaling",
                "vertical_scaling",
                "load_balancing",
                "caching_strategy",
                "database_scaling",
                "service_decomposition"
            ]
        }

        scalability = await self._call_vllm(scalability_query, temperature=0.3)

        return {
            "semantic_type": "scalability_design_result",
            "scalability_strategy": scalability.get("strategy", {}),
            "scaling_approaches": scalability.get("approaches", []),
            "bottleneck_mitigation": scalability.get("bottlenecks", []),
            "implementation_phases": scalability.get("phases", []),
            "cost_projections": scalability.get("costs", {})
        }

    async def _select_technologies(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select appropriate technologies for the project
        """

        requirements = query_csdl.get("requirements", {})
        constraints = query_csdl.get("constraints", [])

        tech_query = {
            "semantic_type": "technology_selection",
            "task": "technology_stack_selection",
            "requirements": requirements,
            "constraints": constraints,
            "evaluate": [
                "programming_languages",
                "frameworks",
                "databases",
                "infrastructure",
                "tooling"
            ],
            "criteria": [
                "performance",
                "scalability",
                "developer_experience",
                "community_support",
                "cost",
                "team_expertise"
            ]
        }

        technologies = await self._call_vllm(tech_query, temperature=0.3)

        return {
            "semantic_type": "technology_selection_result",
            "recommended_stack": technologies.get("stack", {}),
            "alternatives": technologies.get("alternatives", []),
            "rationale": technologies.get("rationale", {}),
            "trade_offs": technologies.get("trade_offs", []),
            "learning_curve": technologies.get("learning", {})
        }

    async def _general_design(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General architecture design"""

        design_query = {
            "semantic_type": "general_architecture",
            "task": "architecture_design",
            "context": query_csdl
        }

        result = await self._call_vllm(design_query, temperature=0.3)

        return result
