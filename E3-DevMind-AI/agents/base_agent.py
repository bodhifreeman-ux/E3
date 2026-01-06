"""
Base Agent Class - Enhanced with State-of-the-Art Patterns

Foundation for all 32 E3 DevMind AI agents.

CRITICAL: All agents communicate ONLY in CSDL (never natural language).
Only Oracle receives translated CSDL from ANLT layer.

Enhanced Features (2026):
- Retry with exponential backoff
- Circuit breaker for cascading failure prevention
- Capability discovery and intelligent routing
- Request deduplication
- Proper timestamp handling
- Confidence-calibrated outputs
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio
import structlog

from csdl.protocol import CSDLMessage, CSDLProtocol, CSDLSemanticStructure
from csdl.vllm_client import CSDLvLLMClient
from csdl.message_bus import csdl_bus

# Import collaboration framework
from agents.collaboration import (
    get_coordinator,
    CollaborationCoordinator,
    RetryConfig,
    AgentError,
    ErrorType,
    AgentCapability,
    AgentRegistry,
    get_timestamp,
    get_timestamp_epoch,
)

# Import system context framework
from agents.system_context import (
    build_system_context,
    get_temperature_for_task,
    AGENT_CONFIGS,
)

# Import Archon integration (optional - may not be available)
try:
    from agents.archon_integration import (
        get_archon_bridge,
        agent_search_knowledge,
        agent_create_task,
        agent_update_task_status,
        ARCHON_CAPABILITIES,
    )
    ARCHON_AVAILABLE = True
except ImportError:
    ARCHON_AVAILABLE = False
    ARCHON_CAPABILITIES = {}

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for all 32 E3 DevMind AI agents

    ALL agents:
    - Communicate ONLY in CSDL (never natural language)
    - Use CSDL-vLLM for inference with retry logic
    - Share common CSDL protocol
    - Have access to knowledge base
    - Can request help from other agents with circuit breaker protection
    - Use state-of-the-art system contexts

    CRITICAL: No agent except Oracle receives natural language.
    All inputs/outputs are pure CSDL.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        vllm_client: CSDLvLLMClient,
        knowledge_base: Any,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent with enhanced capabilities

        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            vllm_client: CSDL-vLLM client
            knowledge_base: E3 knowledge base interface
            config: Agent-specific configuration
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.vllm = vllm_client
        self.kb = knowledge_base
        self.config = config or {}

        # Get collaboration coordinator (singleton)
        self._coordinator: CollaborationCoordinator = get_coordinator()

        # Retry configuration
        self._retry_config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=1.0,
            max_delay_seconds=30.0,
            exponential_base=2.0,
            jitter=True
        )

        # Build state-of-the-art system context
        self.system_context = self._build_system_context()

        # Register capabilities with discovery service
        self._register_capabilities()

        # Register with message bus
        csdl_bus.register_agent(self.agent_id, self._handle_message)

        logger.info(
            "agent_initialized",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            tier=self.system_context.get("tier", "unknown"),
            capabilities=self.system_context.get("capabilities", []),
            timestamp=get_timestamp()
        )

    def _build_system_context(self) -> Dict[str, Any]:
        """
        Build state-of-the-art system context for this agent.

        Uses the centralized system_context module for consistent,
        modern configurations across all agents.

        Returns:
            CSDL-structured system context with reasoning frameworks,
            quality standards, collaboration protocols, and behavioral constraints.
        """
        try:
            return build_system_context(
                self.agent_id,
                custom_overrides=self.config.get("context_overrides")
            )
        except ValueError:
            # Fallback for agents not in config
            logger.warning(
                "agent_config_not_found",
                agent_id=self.agent_id,
                using="fallback_context"
            )
            return self._build_fallback_context()

    def _build_fallback_context(self) -> Dict[str, Any]:
        """Build minimal fallback context for unconfigured agents"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": "general_assistant",
            "tier": 4,
            "capabilities": [],
            "reasoning_mode": "analytical",
            "quality_standards": {
                "min_confidence_threshold": 0.7,
                "require_evidence": True,
                "require_reasoning_chain": True
            },
            "collaboration": {
                "can_request_help": True,
                "preferred_collaborators": [],
                "escalation_path": ["oracle"]
            }
        }

    def _register_capabilities(self):
        """Register this agent's capabilities with the discovery service"""
        capabilities = []
        for cap_name in self.system_context.get("capabilities", []):
            capabilities.append(AgentCapability(
                name=cap_name,
                version="1.0.0",
                description=f"{self.agent_name} capability: {cap_name}",
                input_schema={},
                output_schema={},
                success_rate=0.95,
                avg_latency_ms=2000
            ))

        if capabilities:
            registry = AgentRegistry(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                tier=self.system_context.get("tier", 4),
                capabilities=capabilities,
                availability="available",
                last_heartbeat=datetime.now(timezone.utc)
            )
            self._coordinator.capability_service.register_agent(registry)

    @abstractmethod
    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process CSDL message and return CSDL response

        This is the core processing method every agent must implement.

        Args:
            message: Incoming CSDL message
            context: Additional CSDL context

        Returns:
            CSDLMessage response
        """
        pass

    async def _handle_message(
        self,
        message: CSDLMessage
    ) -> Optional[CSDLMessage]:
        """
        Internal handler for messages from the bus with enhanced error handling

        Args:
            message: Incoming message

        Returns:
            Response message if applicable
        """
        start_time = get_timestamp_epoch()

        try:
            logger.debug(
                "agent_received_message",
                agent_id=self.agent_id,
                message_id=message.message_id,
                sender=message.sender_id,
                type=message.message_type,
                timestamp=get_timestamp()
            )

            # Process the message
            response = await self.process_csdl(message)

            latency_ms = (get_timestamp_epoch() - start_time) * 1000
            logger.debug(
                "agent_processed_message",
                agent_id=self.agent_id,
                message_id=message.message_id,
                response_id=response.message_id if response else None,
                latency_ms=round(latency_ms, 2)
            )

            return response

        except AgentError as e:
            logger.error(
                "agent_error",
                agent_id=self.agent_id,
                message_id=message.message_id,
                error_type=e.error_type.value,
                error=e.message,
                recoverable=e.recoverable
            )

            error_content = CSDLSemanticStructure.create_error_structure(
                error_type=e.error_type.value,
                description=e.message,
                details={
                    "message_id": message.message_id,
                    "recoverable": e.recoverable,
                    **e.details
                }
            )

            return CSDLProtocol.create_error(
                error_csdl=error_content,
                sender_id=self.agent_id,
                in_response_to=message.message_id,
                recipient_id=message.sender_id
            )

        except Exception as e:
            logger.error(
                "agent_message_error",
                agent_id=self.agent_id,
                message_id=message.message_id,
                error=str(e),
                error_type=type(e).__name__
            )

            error_content = CSDLSemanticStructure.create_error_structure(
                error_type="processing_error",
                description=str(e),
                details={"message_id": message.message_id}
            )

            return CSDLProtocol.create_error(
                error_csdl=error_content,
                sender_id=self.agent_id,
                in_response_to=message.message_id,
                recipient_id=message.sender_id
            )

    async def _call_vllm(
        self,
        csdl_input: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: int = 2048,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call CSDL-vLLM with retry logic and context-aware temperature.

        Args:
            csdl_input: CSDL-formatted input
            temperature: Sampling temperature (auto-selected if None)
            max_tokens: Max tokens to generate
            task_type: Type of task for temperature selection
                      (deterministic, analytical, planning, creative)

        Returns:
            CSDL-formatted output
        """
        # Auto-select temperature based on task type if not provided
        if temperature is None:
            if task_type:
                temperature = get_temperature_for_task(self.agent_id, task_type)
            else:
                temperature = self.system_context.get(
                    "temperature_profile", {}
                ).get("default", 0.3)

        async def make_call():
            response = await self.vllm.generate(
                csdl_input=csdl_input,
                temperature=temperature,
                max_tokens=max_tokens,
                agent_context=self.system_context
            )
            return response["csdl_output"]

        # Use retry with backoff
        from agents.collaboration import retry_with_backoff

        try:
            return await retry_with_backoff(
                make_call,
                self._retry_config,
                error_classifier=self._classify_vllm_error
            )
        except AgentError:
            raise
        except Exception as e:
            logger.error(
                "vllm_call_failed",
                agent_id=self.agent_id,
                error=str(e)
            )
            raise AgentError(
                error_type=ErrorType.TRANSIENT,
                message=f"vLLM call failed: {e}",
                details={"original_error": str(e)}
            )

    def _classify_vllm_error(self, error: Exception) -> ErrorType:
        """Classify vLLM errors for retry decisions"""
        error_str = str(error).lower()

        if "timeout" in error_str:
            return ErrorType.TIMEOUT
        elif "out of memory" in error_str or "oom" in error_str:
            return ErrorType.RESOURCE
        elif "invalid" in error_str or "malformed" in error_str:
            return ErrorType.INVALID_INPUT
        elif "connection" in error_str or "network" in error_str:
            return ErrorType.TRANSIENT
        else:
            return ErrorType.TRANSIENT

    async def retrieve_knowledge(
        self,
        query_csdl: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge in CSDL format with error handling

        Args:
            query_csdl: CSDL-formatted query
            limit: Max results

        Returns:
            List of CSDL knowledge entries (empty list on error)
        """
        if not self.kb:
            logger.warning(
                "knowledge_base_not_available",
                agent_id=self.agent_id
            )
            return []

        try:
            results = await self.kb.search_csdl(query_csdl, limit=limit)

            logger.debug(
                "knowledge_retrieved",
                agent_id=self.agent_id,
                query=query_csdl.get("topic", "unknown"),
                results_count=len(results)
            )

            return results

        except Exception as e:
            logger.error(
                "knowledge_retrieval_error",
                agent_id=self.agent_id,
                error=str(e)
            )
            return []

    async def request_agent_help(
        self,
        target_agent_id: str,
        request_csdl: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Request help from another agent (basic version).

        For production use with circuit breaker and retry,
        use request_agent_help_resilient() instead.

        Args:
            target_agent_id: ID of agent to ask
            request_csdl: CSDL request message
            timeout: Timeout in seconds

        Returns:
            CSDL response from target agent
        """
        from csdl.message_bus import request_and_wait

        try:
            response = await request_and_wait(
                target_agent_id=target_agent_id,
                content=request_csdl,
                sender_id=self.agent_id,
                timeout=timeout
            )

            if response:
                logger.debug(
                    "agent_help_received",
                    agent_id=self.agent_id,
                    target=target_agent_id
                )
                return response.content
            else:
                logger.warning(
                    "agent_help_timeout",
                    agent_id=self.agent_id,
                    target_agent=target_agent_id,
                    timeout=timeout
                )
                return None

        except Exception as e:
            logger.error(
                "agent_help_error",
                agent_id=self.agent_id,
                target_agent=target_agent_id,
                error=str(e)
            )
            return None

    async def request_agent_help_resilient(
        self,
        target_agent_id: str,
        request_csdl: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Request help with circuit breaker and retry protection.

        RECOMMENDED: Use this instead of request_agent_help() for production.

        Features:
        - Retry with exponential backoff
        - Circuit breaker to prevent cascading failures
        - Request deduplication

        Args:
            target_agent_id: ID of agent to ask
            request_csdl: CSDL request message
            timeout: Timeout in seconds

        Returns:
            CSDL response from target agent
        """
        return await self._coordinator.request_with_resilience(
            requester_id=self.agent_id,
            target_agent_id=target_agent_id,
            request_csdl=request_csdl,
            request_fn=self.request_agent_help,
            timeout=timeout
        )

    async def request_by_capability(
        self,
        required_capability: str,
        request_csdl: Dict[str, Any],
        timeout: float = 30.0,
        fallback_agents: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Route request to the best agent with required capability.

        Automatically handles routing to the most suitable agent
        and falls back to alternatives if first choice fails.

        Args:
            required_capability: Capability needed (e.g., "code_review")
            request_csdl: CSDL request message
            timeout: Timeout in seconds
            fallback_agents: Additional agents to try as fallbacks

        Returns:
            CSDL response from handling agent
        """
        # Use collaboration from system context
        preferred = self.system_context.get("collaboration", {}).get(
            "preferred_collaborators", []
        )

        # Combine with any explicit fallbacks
        all_fallbacks = list(set((fallback_agents or []) + preferred))

        return await self._coordinator.request_by_capability(
            requester_id=self.agent_id,
            required_capability=required_capability,
            request_csdl=request_csdl,
            request_fn=self.request_agent_help,
            timeout=timeout,
            fallback_agents=all_fallbacks
        )

    async def broadcast_notification(
        self,
        notification_csdl: Dict[str, Any]
    ):
        """
        Broadcast a notification to all agents

        Args:
            notification_csdl: CSDL notification content
        """
        message = CSDLProtocol.create_notification(
            content_csdl={
                **notification_csdl,
                "timestamp": get_timestamp(),
                "sender": self.agent_id
            },
            sender_id=self.agent_id
        )

        await csdl_bus.send_message(message)

    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.system_context.get("capabilities", [])

    def get_role(self) -> str:
        """Get agent role"""
        return self.system_context.get("role", "unknown")

    def get_preferred_collaborators(self) -> List[str]:
        """Get preferred collaborators for this agent"""
        return self.system_context.get("collaboration", {}).get(
            "preferred_collaborators", []
        )

    def get_escalation_path(self) -> List[str]:
        """Get escalation path for this agent"""
        return self.system_context.get("collaboration", {}).get(
            "escalation_path", ["oracle"]
        )

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        return {
            "agent_id": self.agent_id,
            "capabilities": self.get_capabilities(),
            "collaborators": self.get_preferred_collaborators(),
            "escalation_path": self.get_escalation_path(),
            "circuit_breakers": self._coordinator.get_all_circuit_stats()
        }

    # =========================================================================
    # ARCHON INTEGRATION METHODS
    # =========================================================================

    async def archon_search_knowledge(
        self,
        query: str,
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search Archon knowledge base using RAG.

        Agents can use this to access documentation, code examples,
        and other knowledge stored in Archon's vector database.

        Args:
            query: Search query (keep short: 2-5 keywords)
            source_id: Optional source filter

        Returns:
            CSDL-formatted search results
        """
        if not ARCHON_AVAILABLE:
            logger.warning(
                "archon_not_available",
                agent_id=self.agent_id,
                action="search_knowledge"
            )
            return {
                "op": "archon_unavailable",
                "error": "Archon integration not loaded",
                "ts": get_timestamp()
            }

        result = await agent_search_knowledge(query, source_id)
        logger.debug(
            "archon_knowledge_search",
            agent_id=self.agent_id,
            query=query,
            success=result.get("success", False)
        )
        return result

    async def archon_create_task(
        self,
        title: str,
        description: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a task in Archon for tracking work.

        Agents can use this to log tasks they're working on,
        enabling project management across the swarm.

        Args:
            title: Task title
            description: Task description
            project_id: Optional project ID (uses E3 DevMind project if not specified)

        Returns:
            CSDL-formatted task creation result
        """
        if not ARCHON_AVAILABLE:
            logger.warning(
                "archon_not_available",
                agent_id=self.agent_id,
                action="create_task"
            )
            return {
                "op": "archon_unavailable",
                "error": "Archon integration not loaded",
                "ts": get_timestamp()
            }

        result = await agent_create_task(title, description, project_id)
        logger.debug(
            "archon_task_created",
            agent_id=self.agent_id,
            title=title,
            success=result.get("success", False)
        )
        return result

    async def archon_update_task_status(
        self,
        task_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update task status in Archon.

        Status flow: todo -> doing -> review -> done

        Args:
            task_id: Task ID to update
            status: New status (todo, doing, review, done)

        Returns:
            CSDL-formatted update result
        """
        if not ARCHON_AVAILABLE:
            logger.warning(
                "archon_not_available",
                agent_id=self.agent_id,
                action="update_task_status"
            )
            return {
                "op": "archon_unavailable",
                "error": "Archon integration not loaded",
                "ts": get_timestamp()
            }

        result = await agent_update_task_status(task_id, status)
        logger.debug(
            "archon_task_updated",
            agent_id=self.agent_id,
            task_id=task_id,
            status=status,
            success=result.get("success", False)
        )
        return result

    async def archon_search_code(
        self,
        query: str,
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for code examples in Archon knowledge base.

        Args:
            query: Code-related search query
            source_id: Optional source filter

        Returns:
            CSDL-formatted code search results
        """
        if not ARCHON_AVAILABLE:
            return {
                "op": "archon_unavailable",
                "error": "Archon integration not loaded",
                "ts": get_timestamp()
            }

        bridge = get_archon_bridge()
        result = await bridge.search_code_examples(query, source_id)

        return {
            "op": "code_search_result",
            "success": result.success,
            "query": query,
            "results": result.data if result.success else None,
            "error": result.error,
            "ts": get_timestamp()
        }

    def is_archon_available(self) -> bool:
        """Check if Archon integration is available"""
        return ARCHON_AVAILABLE

    def __repr__(self) -> str:
        return f"<{self.agent_name} (ID: {self.agent_id}, Tier: {self.system_context.get('tier', '?')})>"

    def __str__(self) -> str:
        return self.agent_name


class SimpleAgent(BaseAgent):
    """
    Simple agent implementation for testing or basic use cases

    Provides a basic implementation that can be extended easily.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        capabilities: List[str],
        vllm_client: CSDLvLLMClient,
        knowledge_base: Any,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize simple agent

        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            role: Agent role
            capabilities: List of capabilities
            vllm_client: CSDL-vLLM client
            knowledge_base: E3 knowledge base interface
            config: Agent-specific configuration
        """
        self._role = role
        self._capabilities = capabilities
        super().__init__(agent_id, agent_name, vllm_client, knowledge_base, config)

    def _build_system_context(self) -> Dict[str, Any]:
        """Build system context for simple agent"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self._role,
            "tier": 4,
            "capabilities": self._capabilities,
            "description": self.config.get("description", ""),
            "reasoning_mode": "analytical",
            "quality_standards": {
                "min_confidence_threshold": 0.7,
                "require_evidence": True,
                "require_reasoning_chain": True
            },
            "temperature_profile": {
                "default": 0.3
            },
            "collaboration": {
                "can_request_help": True,
                "preferred_collaborators": [],
                "escalation_path": ["oracle"]
            }
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process CSDL message with simple logic

        Args:
            message: Incoming CSDL message
            context: Additional context

        Returns:
            CSDLMessage response
        """
        # Build CSDL input for vLLM
        csdl_input = {
            "task": "process_message",
            "message": message.content,
            "agent_role": self._role,
            "agent_capabilities": self._capabilities,
            "context": context or {},
            "timestamp": get_timestamp()
        }

        # Call vLLM for processing (uses retry logic)
        result = await self._call_vllm(csdl_input, task_type="analytical")

        # Create response with confidence
        confidence = result.get("confidence", 0.8) if isinstance(result, dict) else 0.8

        response_content = CSDLSemanticStructure.create_result(
            result_type="processed_message",
            data=result,
            confidence=confidence
        )

        return CSDLProtocol.create_response(
            content_csdl=response_content,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )
