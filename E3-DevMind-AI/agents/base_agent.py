"""
Base Agent Class

Foundation for all 32 E3 DevMind AI agents.

CRITICAL: All agents communicate ONLY in CSDL (never natural language).
Only Oracle receives translated CSDL from ANLT layer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import structlog
from csdl.protocol import CSDLMessage, CSDLProtocol, CSDLSemanticStructure
from csdl.vllm_client import CSDLvLLMClient
from csdl.message_bus import csdl_bus

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for all 32 E3 DevMind AI agents

    ALL agents:
    - Communicate ONLY in CSDL (never natural language)
    - Use CSDL-vLLM for inference
    - Share common CSDL protocol
    - Have access to knowledge base
    - Can request help from other agents

    CRITICAL: No agent except Oracle receives natural language.
    All inputs/outputs are pure CSDL.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        vllm_client: CSDLvLLMClient,
        knowledge_base: Any,  # Will be typed properly when KB is implemented
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent

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

        # System context in CSDL-friendly format
        # (Will be converted to CSDL for vLLM)
        self.system_context = self._build_system_context()

        # Register with message bus
        csdl_bus.register_agent(self.agent_id, self._handle_message)

        logger.info(
            "agent_initialized",
            agent_id=self.agent_id,
            agent_name=self.agent_name
        )

    @abstractmethod
    def _build_system_context(self) -> Dict[str, Any]:
        """
        Build agent-specific system context

        This is NOT a natural language prompt.
        This is a CSDL-compatible context structure.

        Returns:
            CSDL-structured system context
        """
        pass

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
        Internal handler for messages from the bus

        Args:
            message: Incoming message

        Returns:
            Response message if applicable
        """
        try:
            logger.debug(
                "agent_received_message",
                agent_id=self.agent_id,
                message_id=message.message_id,
                sender=message.sender_id,
                type=message.message_type
            )

            # Process the message
            response = await self.process_csdl(message)

            logger.debug(
                "agent_processed_message",
                agent_id=self.agent_id,
                message_id=message.message_id,
                response_id=response.message_id if response else None
            )

            return response

        except Exception as e:
            logger.error(
                "agent_message_error",
                agent_id=self.agent_id,
                message_id=message.message_id,
                error=str(e)
            )

            # Return error message
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
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Call CSDL-vLLM with pure CSDL input

        Args:
            csdl_input: CSDL-formatted input
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            CSDL-formatted output
        """
        try:
            response = await self.vllm.generate(
                csdl_input=csdl_input,
                temperature=temperature,
                max_tokens=max_tokens,
                agent_context=self.system_context
            )

            return response["csdl_output"]

        except Exception as e:
            logger.error(
                "vllm_call_error",
                agent_id=self.agent_id,
                error=str(e)
            )
            raise

    async def retrieve_knowledge(
        self,
        query_csdl: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge in CSDL format

        Args:
            query_csdl: CSDL-formatted query
            limit: Max results

        Returns:
            List of CSDL knowledge entries
        """
        if not self.kb:
            logger.warning("knowledge_base_not_available", agent_id=self.agent_id)
            return []

        try:
            return await self.kb.search_csdl(query_csdl, limit=limit)
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
        Request help from another agent

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
                return response.content
            else:
                logger.warning(
                    "agent_help_timeout",
                    agent_id=self.agent_id,
                    target_agent=target_agent_id
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

    async def broadcast_notification(
        self,
        notification_csdl: Dict[str, Any]
    ):
        """
        Broadcast a notification to all agents

        Args:
            notification_csdl: CSDL notification content
        """
        from csdl.message_bus import send_to_agent
        from csdl.protocol import MessageType

        message = CSDLProtocol.create_notification(
            content_csdl=notification_csdl,
            sender_id=self.agent_id
        )

        await csdl_bus.send_message(message)

    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities

        Returns:
            List of capability strings
        """
        return self.system_context.get("capabilities", [])

    def get_role(self) -> str:
        """
        Get agent role

        Returns:
            Role string
        """
        return self.system_context.get("role", "unknown")

    def __repr__(self) -> str:
        return f"<{self.agent_name} (ID: {self.agent_id})>"

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
        self.role = role
        self.capabilities = capabilities
        super().__init__(agent_id, agent_name, vllm_client, knowledge_base, config)

    def _build_system_context(self) -> Dict[str, Any]:
        """Build system context for simple agent"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role,
            "capabilities": self.capabilities,
            "description": self.config.get("description", "")
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
            "agent_role": self.role,
            "agent_capabilities": self.capabilities,
            "context": context or {}
        }

        # Call vLLM for processing
        result = await self._call_vllm(csdl_input)

        # Create response
        response_content = CSDLSemanticStructure.create_result(
            result_type="processed_message",
            data=result,
            confidence=0.8
        )

        return CSDLProtocol.create_response(
            content_csdl=response_content,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )
