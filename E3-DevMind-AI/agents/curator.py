"""
Agent #23: CURATOR (Knowledge Organizer)

Organizes E3 knowledge into coherent structures and hierarchies.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class CuratorAgent(BaseAgent):
    """CURATOR - Knowledge Organizer Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="curator",
            agent_name="Curator",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.knowledge_hierarchies: Dict[str, Any] = {}
        self.categories: List[str] = []

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "knowledge_organization",
            "agent_id": "curator",
            "agent_name": "Curator",
            "tier": 5,
            "capabilities": [
                "categorization",
                "hierarchy_building",
                "deduplication",
                "relationship_mapping",
                "taxonomy_creation"
            ],
            "specialization": "knowledge_structure"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process knowledge organization request"""
        query_type = message.content.get("query_type", "organize")

        if query_type == "organize":
            result = await self._organize_knowledge(message.content)
        elif query_type == "categorize":
            result = await self._categorize_content(message.content)
        elif query_type == "deduplicate":
            result = await self._deduplicate(message.content)
        else:
            result = await self._build_hierarchy(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _organize_knowledge(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Organize knowledge into coherent structures"""
        knowledge_items = query_csdl.get("items", [])

        organization_query = {
            "semantic_type": "knowledge_organization",
            "task": "structure_creation",
            "items": knowledge_items,
            "organization_principles": [
                "semantic_similarity",
                "temporal_relationships",
                "hierarchical_dependencies",
                "topic_clustering"
            ]
        }

        structure = await self._call_vllm(organization_query, temperature=0.2)

        # Update internal state
        self.knowledge_hierarchies["latest"] = structure

        return {
            "semantic_type": "organization_result",
            "structure": structure,
            "total_items": len(knowledge_items)
        }

    async def _categorize_content(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize content into appropriate categories"""
        content = query_csdl.get("content", {})

        categorization_query = {
            "semantic_type": "categorization",
            "task": "category_assignment",
            "content": content,
            "existing_categories": self.categories,
            "categorization_strategy": [
                "multi_label_classification",
                "hierarchical_assignment",
                "similarity_based_grouping"
            ]
        }

        categories = await self._call_vllm(categorization_query, temperature=0.2)

        # Update category list
        for cat in categories.get("categories", []):
            if cat not in self.categories:
                self.categories.append(cat)

        return {
            "semantic_type": "categorization_result",
            "categories": categories,
            "confidence": categories.get("confidence", 0.0)
        }

    async def _deduplicate(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate or near-duplicate content"""
        items = query_csdl.get("items", [])

        dedup_query = {
            "semantic_type": "deduplication",
            "task": "duplicate_detection",
            "items": items,
            "similarity_threshold": query_csdl.get("threshold", 0.95),
            "dedup_strategy": [
                "exact_match",
                "semantic_similarity",
                "fuzzy_matching"
            ]
        }

        dedup_result = await self._call_vllm(dedup_query, temperature=0.1)

        return {
            "semantic_type": "deduplication_result",
            "unique_items": dedup_result.get("unique_items", []),
            "duplicates_removed": dedup_result.get("duplicates_removed", 0),
            "duplicate_groups": dedup_result.get("duplicate_groups", [])
        }

    async def _build_hierarchy(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Build hierarchical knowledge structure"""
        items = query_csdl.get("items", [])

        hierarchy_query = {
            "semantic_type": "hierarchy_building",
            "task": "hierarchy_construction",
            "items": items,
            "hierarchy_principles": [
                "parent_child_relationships",
                "abstraction_levels",
                "dependency_ordering"
            ]
        }

        hierarchy = await self._call_vllm(hierarchy_query, temperature=0.2)

        return {
            "semantic_type": "hierarchy_result",
            "hierarchy": hierarchy,
            "depth": hierarchy.get("depth", 0),
            "nodes": hierarchy.get("node_count", 0)
        }
