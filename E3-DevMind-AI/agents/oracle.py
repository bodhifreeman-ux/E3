"""
Oracle Agent - Agent #1

Primary coordinator and entry point for all queries.

CRITICAL ROLE:
- ONLY agent that interfaces with ANLT translation layer
- Receives CSDL from ANLT (human input translated)
- Routes to appropriate agents
- Coordinates multi-agent responses
- Synthesizes final answer
- Returns CSDL to ANLT (translated to human output)

All 31 other agents work in pure CSDL internally and never touch ANLT.
"""

from typing import Dict, Any, Optional, List
import asyncio
import structlog
from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage, CSDLProtocol, CSDLSemanticStructure, MessageType
from csdl.vllm_client import CSDLvLLMClient
from csdl.message_bus import request_and_wait

logger = structlog.get_logger()


class OracleAgent(BaseAgent):
    """
    Agent #1: ORACLE

    Main coordinator and entry point for all queries.

    Responsibilities:
    - Receives CSDL from ANLT translation layer
    - Routes to appropriate agents
    - Coordinates multi-agent responses
    - Synthesizes final answer
    - Returns CSDL to ANLT

    CRITICAL: This is the ONLY agent that interfaces with ANLT.
    All other 31 agents work in pure CSDL internally.
    """

    def __init__(
        self,
        vllm_client: CSDLvLLMClient,
        knowledge_base: Any,
        agent_registry: Dict[str, BaseAgent],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Oracle agent

        Args:
            vllm_client: CSDL-vLLM client
            knowledge_base: E3 knowledge base
            agent_registry: Registry of all other agents
            config: Configuration
        """
        self.agent_registry = agent_registry  # Access to all 31 other agents

        super().__init__(
            agent_id="oracle",
            agent_name="Oracle",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

        logger.info("oracle_agent_initialized", agent_count=len(agent_registry))

    def _build_system_context(self) -> Dict[str, Any]:
        """
        Oracle's system context in CSDL-compatible format
        """
        return {
            "role": "primary_coordinator",
            "agent_id": "oracle",
            "agent_name": "Oracle",
            "tier": 1,
            "capabilities": [
                "task_routing",
                "agent_coordination",
                "response_synthesis",
                "decision_making",
                "multi_agent_orchestration"
            ],
            "available_agents": [
                {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "role": agent.get_role(),
                    "capabilities": agent.get_capabilities()
                }
                for agent in self.agent_registry.values()
            ],
            "responsibilities": {
                "receive": "csdl_from_anlt",
                "coordinate": "agent_swarm",
                "synthesize": "multi_agent_responses",
                "return": "csdl_to_anlt"
            },
            "interface": "anlt_translation_layer"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Main processing flow for Oracle

        Flow:
        1. Analyze CSDL query
        2. Determine which agents needed
        3. Coordinate agent responses (parallel/sequential)
        4. Synthesize into final answer
        5. Return CSDL

        Args:
            message: CSDL message (from ANLT or internal)
            context: Additional context

        Returns:
            Synthesized CSDL response
        """
        try:
            logger.info(
                "oracle_processing_query",
                message_id=message.message_id,
                sender=message.sender_id
            )

            # Step 1: Analyze query and determine routing
            routing_decision = await self._determine_routing(message)

            logger.debug(
                "oracle_routing_determined",
                agents=routing_decision["agents"],
                sequence=routing_decision["sequence"]
            )

            # Step 2: Coordinate agent responses
            agent_responses = await self._coordinate_agents(
                message,
                routing_decision["agents"],
                routing_decision["sequence"]
            )

            logger.debug(
                "oracle_agents_coordinated",
                response_count=len(agent_responses)
            )

            # Step 3: Synthesize final response
            final_response = await self._synthesize_responses(
                message,
                agent_responses,
                routing_decision
            )

            logger.info(
                "oracle_query_completed",
                message_id=message.message_id,
                agents_involved=len(agent_responses)
            )

            return final_response

        except Exception as e:
            logger.error(
                "oracle_processing_error",
                message_id=message.message_id,
                error=str(e)
            )

            # Return error response
            error_content = CSDLSemanticStructure.create_error_structure(
                error_type="oracle_processing_error",
                description=str(e),
                details={"message_id": message.message_id}
            )

            return CSDLProtocol.create_error(
                error_csdl=error_content,
                sender_id=self.agent_id,
                in_response_to=message.message_id,
                recipient_id=message.sender_id
            )

    async def _determine_routing(
        self,
        message: CSDLMessage
    ) -> Dict[str, Any]:
        """
        Determine which agents should handle this query

        Uses Oracle's intelligence to route optimally.

        Args:
            message: Incoming CSDL message

        Returns:
            Routing decision with agent IDs and execution sequence
        """
        # Build routing query in CSDL
        routing_query = {
            "semantic_type": "routing_analysis",
            "task": "determine_agent_routing",
            "query": message.content,
            "available_agents": [
                {
                    "id": agent.agent_id,
                    "name": agent.agent_name,
                    "role": agent.get_role(),
                    "capabilities": agent.get_capabilities()
                }
                for agent in self.agent_registry.values()
            ],
            "instructions": {
                "analyze": "query_intent_and_requirements",
                "select": "optimal_agents_for_task",
                "determine": "parallel_or_sequential_execution",
                "prioritize": "efficiency_and_accuracy"
            }
        }

        # Ask vLLM to determine routing
        routing_response = await self._call_vllm(
            routing_query,
            temperature=0.3  # Lower temperature for routing decisions
        )

        # Extract agent IDs and sequence
        agents = routing_response.get("selected_agents", [])
        sequence = routing_response.get("execution_sequence", "parallel")

        # Fallback: if no agents selected, use default routing
        if not agents:
            agents = self._default_routing(message)
            sequence = "parallel"

        return {
            "agents": agents,
            "sequence": sequence,
            "reasoning": routing_response.get("reasoning", "")
        }

    def _default_routing(self, message: CSDLMessage) -> List[str]:
        """
        Default routing logic when vLLM doesn't select agents

        Args:
            message: Incoming message

        Returns:
            List of default agent IDs
        """
        # Extract intent
        intent = CSDLProtocol.extract_intent(message)

        # Default routing based on common patterns
        if "code" in intent or "implementation" in intent:
            return ["architect", "forge", "craftsman"]
        elif "test" in intent or "quality" in intent:
            return ["scientist", "craftsman"]
        elif "security" in intent:
            return ["sentinel", "critic"]
        elif "knowledge" in intent or "search" in intent or "find" in intent:
            return ["oracle_kb", "librarian"]
        elif "predict" in intent or "risk" in intent:
            return ["prophet", "strategist"]
        elif "analyze" in intent:
            return ["investigator", "detective"]
        elif "design" in intent or "architecture" in intent:
            return ["architect", "strategist"]
        else:
            # General query - use knowledge and analysis agents
            return ["oracle_kb", "investigator", "synthesizer"]

    async def _coordinate_agents(
        self,
        message: CSDLMessage,
        agent_ids: List[str],
        sequence: str
    ) -> List[Dict[str, Any]]:
        """
        Coordinate multiple agents

        Args:
            message: Original CSDL message
            agent_ids: List of agent IDs to invoke
            sequence: 'parallel' or 'sequential'

        Returns:
            List of agent responses in CSDL
        """
        if sequence == "parallel":
            return await self._execute_parallel(message, agent_ids)
        else:
            return await self._execute_sequential(message, agent_ids)

    async def _execute_parallel(
        self,
        message: CSDLMessage,
        agent_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Execute agents in parallel

        Args:
            message: CSDL message
            agent_ids: Agent IDs to execute

        Returns:
            List of responses
        """
        # Create tasks for all agents
        tasks = []
        for agent_id in agent_ids:
            if agent_id in self.agent_registry:
                task = self._query_agent(agent_id, message)
                tasks.append(task)
            else:
                logger.warning("agent_not_found", agent_id=agent_id)

        # Execute in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors and format results
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(
                    "agent_execution_error",
                    agent_id=agent_ids[i] if i < len(agent_ids) else "unknown",
                    error=str(response)
                )
            elif response:
                results.append({
                    "agent_id": agent_ids[i] if i < len(agent_ids) else "unknown",
                    "response": response
                })

        return results

    async def _execute_sequential(
        self,
        message: CSDLMessage,
        agent_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Execute agents sequentially, building context

        Args:
            message: CSDL message
            agent_ids: Agent IDs to execute

        Returns:
            List of responses
        """
        results = []
        cumulative_context = {
            "original_query": message.content,
            "previous_responses": []
        }

        for agent_id in agent_ids:
            if agent_id not in self.agent_registry:
                logger.warning("agent_not_found", agent_id=agent_id)
                continue

            try:
                # Create message with cumulative context
                contextualized_message = CSDLMessage(
                    message_type=message.message_type,
                    sender_id=self.agent_id,
                    recipient_id=agent_id,
                    content=message.content,
                    metadata={
                        "context": cumulative_context,
                        "sequence_position": len(results) + 1,
                        "total_agents": len(agent_ids)
                    }
                )

                response = await self._query_agent(agent_id, contextualized_message)

                if response:
                    result = {
                        "agent_id": agent_id,
                        "response": response
                    }
                    results.append(result)

                    # Add to cumulative context
                    cumulative_context["previous_responses"].append(result)

            except Exception as e:
                logger.error(
                    "sequential_agent_error",
                    agent_id=agent_id,
                    error=str(e)
                )

        return results

    async def _query_agent(
        self,
        agent_id: str,
        message: CSDLMessage,
        timeout: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Query a specific agent

        Args:
            agent_id: Agent to query
            message: Message to send
            timeout: Timeout in seconds

        Returns:
            Agent response content
        """
        try:
            agent = self.agent_registry.get(agent_id)
            if not agent:
                return None

            # Send request and wait for response
            response = await request_and_wait(
                target_agent_id=agent_id,
                content=message.content,
                sender_id=self.agent_id,
                timeout=timeout
            )

            if response:
                return response.content
            else:
                logger.warning("agent_timeout", agent_id=agent_id)
                return None

        except Exception as e:
            logger.error("agent_query_error", agent_id=agent_id, error=str(e))
            return None

    async def _synthesize_responses(
        self,
        original_message: CSDLMessage,
        agent_responses: List[Dict[str, Any]],
        routing_decision: Dict[str, Any]
    ) -> CSDLMessage:
        """
        Synthesize multiple agent responses into one coherent answer

        Args:
            original_message: Original query
            agent_responses: List of agent responses
            routing_decision: Routing decision info

        Returns:
            Synthesized CSDL message
        """
        # Build synthesis request
        synthesis_request = {
            "semantic_type": "synthesis_request",
            "task": "synthesize_agent_responses",
            "original_query": original_message.content,
            "agent_responses": agent_responses,
            "routing_info": routing_decision,
            "instructions": {
                "combine": "insights_from_all_agents",
                "resolve": "conflicts_or_contradictions",
                "prioritize": "accuracy_and_completeness",
                "format": "coherent_unified_response"
            }
        }

        # Use Synthesizer agent if available
        if "synthesizer" in self.agent_registry:
            try:
                synthesis = await self._query_agent(
                    "synthesizer",
                    CSDLMessage(
                        message_type=MessageType.REQUEST,
                        sender_id=self.agent_id,
                        recipient_id="synthesizer",
                        content=synthesis_request
                    )
                )

                if synthesis:
                    return CSDLProtocol.create_response(
                        content_csdl=synthesis,
                        sender_id=self.agent_id,
                        in_response_to=original_message.message_id,
                        recipient_id=original_message.sender_id,
                        metadata={
                            "agents_involved": len(agent_responses),
                            "agent_ids": [r["agent_id"] for r in agent_responses],
                            "synthesis_quality": "high"
                        }
                    )
            except Exception as e:
                logger.error("synthesizer_error", error=str(e))

        # Fallback: Oracle does synthesis directly using vLLM
        synthesis = await self._call_vllm(
            synthesis_request,
            temperature=0.5
        )

        return CSDLProtocol.create_response(
            content_csdl=synthesis,
            sender_id=self.agent_id,
            in_response_to=original_message.message_id,
            recipient_id=original_message.sender_id,
            metadata={
                "agents_involved": len(agent_responses),
                "agent_ids": [r["agent_id"] for r in agent_responses],
                "synthesis_quality": "medium",
                "synthesized_by": "oracle"
            }
        )

    async def query_from_human(
        self,
        csdl_from_anlt: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query from human (already translated to CSDL by ANLT)

        This is the main entry point for human queries.

        Args:
            csdl_from_anlt: CSDL-formatted query from ANLT translation
            metadata: Additional metadata

        Returns:
            CSDL response (to be translated back to human by ANLT)
        """
        # Create CSDL message
        message = CSDLMessage(
            message_type=MessageType.QUERY,
            sender_id="anlt",
            recipient_id=self.agent_id,
            content=csdl_from_anlt,
            metadata=metadata or {}
        )

        # Process through normal flow
        response = await self.process_csdl(message)

        # Return CSDL content for ANLT to translate
        return response.content
