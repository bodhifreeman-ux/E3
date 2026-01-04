"""
Agent #11: CARTOGRAPHER (Knowledge Mapper)

Organizes and maps all E3 knowledge into coherent structures.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class CartographerAgent(BaseAgent):
    """
    CARTOGRAPHER - Knowledge Mapper Agent

    Capabilities:
    - Knowledge graph construction
    - Relationship mapping
    - Concept hierarchy building
    - Gap identification
    - Knowledge structure optimization
    - Semantic organization
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="cartographer",
            agent_name="Cartographer",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "knowledge_organization",
            "agent_id": "cartographer",
            "agent_name": "Cartographer",
            "tier": 3,
            "capabilities": [
                "knowledge_graph_construction",
                "relationship_mapping",
                "concept_hierarchy_building",
                "gap_identification",
                "structure_optimization",
                "semantic_organization"
            ],
            "specialization": "information_architecture",
            "perspective": "structural_and_relational"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Map and organize knowledge"""

        query_type = message.content.get("query_type", "knowledge_mapping")

        logger.info(
            "cartographer_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "knowledge_mapping":
            result = await self._map_knowledge(message.content)
        elif query_type == "relationship_mapping":
            result = await self._map_relationships(message.content)
        elif query_type == "hierarchy_building":
            result = await self._build_hierarchy(message.content)
        elif query_type == "gap_identification":
            result = await self._identify_gaps(message.content)
        elif query_type == "structure_optimization":
            result = await self._optimize_structure(message.content)
        else:
            result = await self._general_mapping(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _map_knowledge(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create knowledge map/graph for a domain
        """

        scope = query_csdl.get("scope", "all")

        # Retrieve knowledge in scope
        knowledge = await self.retrieve_knowledge(
            {"scope": scope},
            limit=50
        )

        mapping_query = {
            "semantic_type": "knowledge_mapping",
            "task": "knowledge_mapping",
            "scope": scope,
            "knowledge_data": knowledge,
            "create": [
                "concept_graph",
                "relationships",
                "clusters",
                "hierarchies",
                "gaps"
            ],
            "format": "graph_structure"
        }

        knowledge_map = await self._call_vllm(mapping_query, temperature=0.3)

        return {
            "semantic_type": "knowledge_map_result",
            "knowledge_graph": knowledge_map.get("graph", {}),
            "nodes": knowledge_map.get("nodes", []),
            "edges": knowledge_map.get("edges", []),
            "clusters": knowledge_map.get("clusters", []),
            "hierarchies": knowledge_map.get("hierarchies", []),
            "key_relationships": knowledge_map.get("relationships", []),
            "knowledge_gaps": knowledge_map.get("gaps", [])
        }

    async def _map_relationships(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map relationships between concepts/entities
        """

        entities = query_csdl.get("entities", [])

        relationship_query = {
            "semantic_type": "relationship_mapping",
            "task": "relationship_mapping",
            "entities": entities,
            "identify": [
                "direct_relationships",
                "indirect_relationships",
                "causal_relationships",
                "dependency_relationships",
                "hierarchical_relationships"
            ]
        }

        relationships = await self._call_vllm(relationship_query, temperature=0.3)

        return {
            "semantic_type": "relationship_map_result",
            "relationships": relationships.get("relationships", []),
            "relationship_types": relationships.get("types", {}),
            "strength": relationships.get("strength", {}),
            "directionality": relationships.get("direction", {}),
            "graph_representation": relationships.get("graph", {})
        }

    async def _build_hierarchy(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build concept hierarchy
        """

        domain = query_csdl.get("domain", "")

        # Get domain knowledge
        domain_knowledge = await self.retrieve_knowledge(
            {"domain": domain},
            limit=40
        )

        hierarchy_query = {
            "semantic_type": "hierarchy_building",
            "task": "concept_hierarchy_building",
            "domain": domain,
            "knowledge": domain_knowledge,
            "create": [
                "top_level_concepts",
                "sub_concepts",
                "relationships",
                "depth_levels",
                "taxonomy"
            ]
        }

        hierarchy = await self._call_vllm(hierarchy_query, temperature=0.3)

        return {
            "semantic_type": "hierarchy_result",
            "hierarchy": hierarchy.get("hierarchy", {}),
            "levels": hierarchy.get("levels", []),
            "taxonomy": hierarchy.get("taxonomy", {}),
            "parent_child_relationships": hierarchy.get("relationships", []),
            "depth": hierarchy.get("depth", 0)
        }

    async def _identify_gaps(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify gaps in knowledge coverage
        """

        domain = query_csdl.get("domain", "")

        # Get existing knowledge
        existing = await self.retrieve_knowledge(
            {"domain": domain},
            limit=30
        )

        gap_query = {
            "semantic_type": "gap_identification",
            "task": "knowledge_gap_identification",
            "domain": domain,
            "existing_knowledge": existing,
            "expected_coverage": query_csdl.get("expected_coverage", []),
            "identify": [
                "missing_topics",
                "incomplete_coverage",
                "outdated_information",
                "inconsistencies",
                "areas_needing_expansion"
            ]
        }

        gaps = await self._call_vllm(gap_query, temperature=0.3)

        return {
            "semantic_type": "gap_identification_result",
            "knowledge_gaps": gaps.get("gaps", []),
            "missing_topics": gaps.get("missing", []),
            "incomplete_areas": gaps.get("incomplete", []),
            "priority_gaps": gaps.get("priority", []),
            "recommendations": gaps.get("recommendations", [])
        }

    async def _optimize_structure(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize knowledge structure and organization
        """

        current_structure = query_csdl.get("current_structure", {})

        optimization_query = {
            "semantic_type": "structure_optimization",
            "task": "knowledge_structure_optimization",
            "current_structure": current_structure,
            "optimize_for": [
                "findability",
                "coherence",
                "completeness",
                "maintainability",
                "scalability"
            ]
        }

        optimization = await self._call_vllm(optimization_query, temperature=0.3)

        return {
            "semantic_type": "structure_optimization_result",
            "optimized_structure": optimization.get("structure", {}),
            "improvements": optimization.get("improvements", []),
            "reorganization_plan": optimization.get("plan", []),
            "expected_benefits": optimization.get("benefits", []),
            "implementation_steps": optimization.get("steps", [])
        }

    async def _general_mapping(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General knowledge mapping"""

        mapping_query = {
            "semantic_type": "general_mapping",
            "task": "knowledge_mapping",
            "context": query_csdl
        }

        result = await self._call_vllm(mapping_query, temperature=0.3)

        return result
