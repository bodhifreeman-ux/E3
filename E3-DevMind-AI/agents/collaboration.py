"""
Agent Collaboration Framework

This module provides state-of-the-art inter-agent collaboration patterns
identified as the #1 improvement opportunity across all 32 E3 DevMind agents.

Key Features:
- Retry logic with exponential backoff
- Circuit breaker pattern to prevent cascading failures
- Agent capability discovery and matching
- Request deduplication
- Distributed tracing support
- Confidence-aware routing

Based on comprehensive analysis of modern multi-agent system best practices (2025-2026).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Awaitable
import asyncio
import hashlib
import json
import time
import structlog

logger = structlog.get_logger()


# =============================================================================
# ERROR CLASSIFICATION
# =============================================================================

class ErrorType(Enum):
    """Classification of errors for intelligent handling"""
    TRANSIENT = "transient"      # Retry with backoff
    PERMANENT = "permanent"      # Don't retry, escalate
    RESOURCE = "resource"        # Wait longer, then retry
    TIMEOUT = "timeout"          # Backoff and retry
    INVALID_INPUT = "invalid"    # Don't retry, fix input


class AgentError(Exception):
    """
    Rich exception with error classification for intelligent recovery.

    Attributes:
        error_type: Classification for recovery strategy
        message: Human-readable error description
        details: Additional context for debugging
        recoverable: Whether error can be recovered from
    """
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.recoverable = recoverable
        super().__init__(message)


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreaker:
    """
    Prevents cascading failures by tracking error rates and temporarily
    stopping requests to failing services.

    Transitions:
    - CLOSED -> OPEN: When failure_count >= failure_threshold
    - OPEN -> HALF_OPEN: After reset_timeout_seconds has passed
    - HALF_OPEN -> CLOSED: On successful request
    - HALF_OPEN -> OPEN: On failed request
    """
    name: str
    failure_threshold: int = 5
    reset_timeout_seconds: int = 60

    # State tracking
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    success_count: int = 0
    total_calls: int = 0

    def record_success(self):
        """Record successful call"""
        self.total_calls += 1
        self.success_count += 1
        self.failure_count = 0

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info(
                "circuit_breaker_closed",
                name=self.name,
                reason="successful_test_request"
            )

    def record_failure(self):
        """Record failed call"""
        self.total_calls += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "circuit_breaker_opened",
                name=self.name,
                failure_count=self.failure_count,
                threshold=self.failure_threshold
            )
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "circuit_breaker_reopened",
                name=self.name,
                reason="failed_test_request"
            )

    def can_execute(self) -> bool:
        """Check if circuit allows execution"""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time is None:
                return True

            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.reset_timeout_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(
                    "circuit_breaker_half_open",
                    name=self.name,
                    elapsed_seconds=elapsed
                )
                return True
            return False

        # HALF_OPEN allows one test request
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        success_rate = (
            self.success_count / self.total_calls
            if self.total_calls > 0 else 1.0
        )
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_rate": round(success_rate, 3),
            "total_calls": self.total_calls,
            "last_failure": (
                datetime.fromtimestamp(self.last_failure_time).isoformat()
                if self.last_failure_time else None
            )
        }


# =============================================================================
# RETRY LOGIC
# =============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry with exponential backoff"""
    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        delay = self.initial_delay_seconds * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay_seconds)

        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())

        return delay


async def retry_with_backoff(
    func: Callable[[], Awaitable[Any]],
    config: RetryConfig,
    error_classifier: Optional[Callable[[Exception], ErrorType]] = None
) -> Any:
    """
    Execute function with exponential backoff retry.

    Args:
        func: Async function to execute
        config: Retry configuration
        error_classifier: Function to classify errors (default: all are transient)

    Returns:
        Result of successful function call

    Raises:
        AgentError: If all retries exhausted or permanent error encountered
    """
    last_error = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func()

        except Exception as e:
            last_error = e
            error_type = (
                error_classifier(e) if error_classifier
                else ErrorType.TRANSIENT
            )

            # Don't retry permanent or invalid input errors
            if error_type in (ErrorType.PERMANENT, ErrorType.INVALID_INPUT):
                logger.error(
                    "retry_permanent_error",
                    error=str(e),
                    error_type=error_type.value,
                    attempt=attempt
                )
                raise AgentError(
                    error_type=error_type,
                    message=str(e),
                    recoverable=False
                )

            # Last attempt, don't retry
            if attempt >= config.max_retries:
                break

            delay = config.get_delay(attempt)
            logger.warning(
                "retry_attempt",
                attempt=attempt + 1,
                max_retries=config.max_retries,
                delay_seconds=round(delay, 2),
                error=str(e)
            )

            await asyncio.sleep(delay)

    # All retries exhausted
    raise AgentError(
        error_type=ErrorType.TRANSIENT,
        message=f"All {config.max_retries} retries exhausted: {last_error}",
        details={"last_error": str(last_error)},
        recoverable=False
    )


# =============================================================================
# CAPABILITY DISCOVERY
# =============================================================================

@dataclass
class AgentCapability:
    """Formal declaration of an agent capability"""
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    avg_latency_ms: float = 1000.0
    success_rate: float = 0.95
    min_confidence: float = 0.7

    def matches_requirement(self, required_capability: str) -> float:
        """Score how well this capability matches a requirement (0-1)"""
        # Exact match
        if self.name == required_capability:
            return 1.0

        # Partial match (capability contains requirement)
        if required_capability in self.name:
            return 0.8

        # No match
        return 0.0


@dataclass
class AgentRegistry:
    """Registry of agent capabilities for intelligent routing"""
    agent_id: str
    agent_name: str
    tier: int
    capabilities: List[AgentCapability] = field(default_factory=list)
    availability: str = "available"  # available, degraded, unavailable
    last_heartbeat: Optional[datetime] = None

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability"""
        return any(
            cap.name == capability_name
            for cap in self.capabilities
        )

    def get_capability(self, capability_name: str) -> Optional[AgentCapability]:
        """Get specific capability details"""
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap
        return None


class CapabilityDiscoveryService:
    """
    Central service for discovering agent capabilities.

    Enables intelligent routing by matching requests to the best-suited agents.
    """

    def __init__(self):
        self._registries: Dict[str, AgentRegistry] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> agent_ids

    def register_agent(self, registry: AgentRegistry):
        """Register an agent with its capabilities"""
        self._registries[registry.agent_id] = registry

        # Update capability index
        for cap in registry.capabilities:
            if cap.name not in self._capability_index:
                self._capability_index[cap.name] = []
            if registry.agent_id not in self._capability_index[cap.name]:
                self._capability_index[cap.name].append(registry.agent_id)

        logger.info(
            "agent_registered",
            agent_id=registry.agent_id,
            capabilities=[cap.name for cap in registry.capabilities]
        )

    def find_agents_for_capability(
        self,
        capability_name: str,
        min_success_rate: float = 0.8
    ) -> List[AgentRegistry]:
        """
        Find agents that can handle a capability.

        Args:
            capability_name: Required capability
            min_success_rate: Minimum acceptable success rate

        Returns:
            List of matching agent registries, sorted by suitability
        """
        agent_ids = self._capability_index.get(capability_name, [])

        matching = []
        for agent_id in agent_ids:
            registry = self._registries.get(agent_id)
            if not registry:
                continue

            cap = registry.get_capability(capability_name)
            if cap and cap.success_rate >= min_success_rate:
                matching.append(registry)

        # Sort by success rate (descending), then latency (ascending)
        matching.sort(
            key=lambda r: (
                -r.get_capability(capability_name).success_rate,
                r.get_capability(capability_name).avg_latency_ms
            )
        )

        return matching

    def get_best_agent_for_task(
        self,
        required_capabilities: List[str],
        exclude_agents: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Find the best agent for a task requiring multiple capabilities.

        Args:
            required_capabilities: List of required capabilities
            exclude_agents: Agents to exclude (e.g., already tried and failed)

        Returns:
            Best matching agent_id or None
        """
        exclude_set = set(exclude_agents or [])

        # Score each agent
        scores: Dict[str, float] = {}
        for agent_id, registry in self._registries.items():
            if agent_id in exclude_set:
                continue

            if registry.availability == "unavailable":
                continue

            # Calculate match score
            total_score = 0.0
            for cap_name in required_capabilities:
                cap = registry.get_capability(cap_name)
                if cap:
                    total_score += cap.success_rate

            if total_score > 0:
                scores[agent_id] = total_score / len(required_capabilities)

        if not scores:
            return None

        # Return highest scoring agent
        return max(scores, key=scores.get)


# =============================================================================
# REQUEST DEDUPLICATION
# =============================================================================

class RequestDeduplicator:
    """
    Prevents duplicate requests from being processed multiple times.

    Uses semantic hashing to identify equivalent requests.
    """

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def _hash_request(self, request: Dict[str, Any]) -> str:
        """Create semantic hash of request"""
        # Extract semantic fields (ignore metadata like timestamps)
        semantic_fields = {
            k: v for k, v in request.items()
            if not k.startswith("_") and k not in ("timestamp", "trace_id")
        }

        content = json.dumps(semantic_fields, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_cached(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result for request if available and fresh"""
        async with self._lock:
            request_hash = self._hash_request(request)

            if request_hash not in self._cache:
                return None

            cached = self._cache[request_hash]
            age = time.time() - cached["timestamp"]

            if age > self.ttl_seconds:
                del self._cache[request_hash]
                return None

            logger.debug(
                "request_cache_hit",
                request_hash=request_hash,
                age_seconds=round(age, 1)
            )
            return cached["result"]

    async def cache_result(
        self,
        request: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """Cache result for future duplicate requests"""
        async with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache,
                    key=lambda k: self._cache[k]["timestamp"]
                )
                del self._cache[oldest_key]

            request_hash = self._hash_request(request)
            self._cache[request_hash] = {
                "result": result,
                "timestamp": time.time()
            }


# =============================================================================
# COLLABORATION COORDINATOR
# =============================================================================

class CollaborationCoordinator:
    """
    Orchestrates intelligent collaboration between agents.

    Features:
    - Capability-aware routing
    - Circuit breaker protection
    - Retry with exponential backoff
    - Request deduplication
    - Distributed tracing
    """

    def __init__(self):
        self.capability_service = CapabilityDiscoveryService()
        self.deduplicator = RequestDeduplicator()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._default_retry_config = RetryConfig()

    def get_circuit_breaker(self, agent_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for an agent"""
        if agent_id not in self._circuit_breakers:
            self._circuit_breakers[agent_id] = CircuitBreaker(name=agent_id)
        return self._circuit_breakers[agent_id]

    async def request_with_resilience(
        self,
        requester_id: str,
        target_agent_id: str,
        request_csdl: Dict[str, Any],
        request_fn: Callable[[str, Dict[str, Any], float], Awaitable[Optional[Dict[str, Any]]]],
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a resilient request with circuit breaker and retry.

        Args:
            requester_id: ID of requesting agent
            target_agent_id: ID of target agent
            request_csdl: CSDL request content
            request_fn: Actual request function (agent.request_agent_help)
            timeout: Request timeout
            retry_config: Retry configuration (uses default if None)

        Returns:
            Response from target agent or None if all attempts fail
        """
        circuit = self.get_circuit_breaker(target_agent_id)
        config = retry_config or self._default_retry_config

        # Check circuit breaker
        if not circuit.can_execute():
            logger.warning(
                "circuit_breaker_blocked",
                requester=requester_id,
                target=target_agent_id,
                circuit_state=circuit.state.value
            )
            return None

        # Check cache for duplicate request
        cached = await self.deduplicator.get_cached(request_csdl)
        if cached is not None:
            return cached

        # Define the request function for retry
        async def make_request():
            response = await request_fn(target_agent_id, request_csdl, timeout)
            if response is None:
                raise AgentError(
                    error_type=ErrorType.TIMEOUT,
                    message=f"No response from {target_agent_id}"
                )
            return response

        try:
            result = await retry_with_backoff(make_request, config)
            circuit.record_success()

            # Cache successful result
            await self.deduplicator.cache_result(request_csdl, result)

            return result

        except AgentError as e:
            circuit.record_failure()
            logger.error(
                "resilient_request_failed",
                requester=requester_id,
                target=target_agent_id,
                error=e.message,
                error_type=e.error_type.value
            )
            return None

    async def request_by_capability(
        self,
        requester_id: str,
        required_capability: str,
        request_csdl: Dict[str, Any],
        request_fn: Callable[[str, Dict[str, Any], float], Awaitable[Optional[Dict[str, Any]]]],
        timeout: float = 30.0,
        fallback_agents: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Route request to best agent with the required capability.

        Automatically falls back to other capable agents if first choice fails.

        Args:
            requester_id: ID of requesting agent
            required_capability: Capability required to handle request
            request_csdl: CSDL request content
            request_fn: Actual request function
            timeout: Request timeout
            fallback_agents: Additional agents to try as fallbacks

        Returns:
            Response from handling agent or None
        """
        # Find capable agents
        capable_agents = self.capability_service.find_agents_for_capability(
            required_capability
        )

        # Add fallback agents
        tried_agents = set()
        all_candidates = [r.agent_id for r in capable_agents]
        if fallback_agents:
            all_candidates.extend(
                a for a in fallback_agents if a not in all_candidates
            )

        for agent_id in all_candidates:
            if agent_id in tried_agents:
                continue
            tried_agents.add(agent_id)

            # Check circuit breaker before trying
            circuit = self.get_circuit_breaker(agent_id)
            if not circuit.can_execute():
                continue

            result = await self.request_with_resilience(
                requester_id=requester_id,
                target_agent_id=agent_id,
                request_csdl=request_csdl,
                request_fn=request_fn,
                timeout=timeout
            )

            if result is not None:
                return result

        logger.error(
            "no_capable_agent_available",
            requester=requester_id,
            capability=required_capability,
            tried_agents=list(tried_agents)
        )
        return None

    def get_all_circuit_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return [cb.get_stats() for cb in self._circuit_breakers.values()]


# =============================================================================
# GLOBAL COORDINATOR INSTANCE
# =============================================================================

# Singleton coordinator for use across all agents
_coordinator: Optional[CollaborationCoordinator] = None


def get_coordinator() -> CollaborationCoordinator:
    """Get the global collaboration coordinator"""
    global _coordinator
    if _coordinator is None:
        _coordinator = CollaborationCoordinator()
    return _coordinator


# =============================================================================
# ENHANCED BASE AGENT MIXIN
# =============================================================================

class CollaborativeAgentMixin:
    """
    Mixin class that adds collaboration capabilities to any agent.

    Usage:
        class MyAgent(BaseAgent, CollaborativeAgentMixin):
            pass

    Provides:
        - request_agent_help_resilient(): Retry + circuit breaker
        - request_by_capability(): Intelligent routing
        - register_capabilities(): Declare agent capabilities
    """

    def __init__(self):
        self._coordinator = get_coordinator()
        self._capabilities: List[AgentCapability] = []

    def register_capabilities(self, capabilities: List[AgentCapability]):
        """Register this agent's capabilities with the discovery service"""
        self._capabilities = capabilities

        registry = AgentRegistry(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            tier=self.system_context.get("tier", 5),
            capabilities=capabilities,
            availability="available",
            last_heartbeat=datetime.now(timezone.utc)
        )

        self._coordinator.capability_service.register_agent(registry)

    async def request_agent_help_resilient(
        self,
        target_agent_id: str,
        request_csdl: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Request help with retry logic and circuit breaker protection.

        Replacement for base request_agent_help() with production-grade resilience.
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

        Automatically handles fallback if first choice fails.
        """
        return await self._coordinator.request_by_capability(
            requester_id=self.agent_id,
            required_capability=required_capability,
            request_csdl=request_csdl,
            request_fn=self.request_agent_help,
            timeout=timeout,
            fallback_agents=fallback_agents
        )

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics for this agent"""
        return {
            "agent_id": self.agent_id,
            "capabilities": [cap.name for cap in self._capabilities],
            "circuit_breakers": self._coordinator.get_all_circuit_stats()
        }


# =============================================================================
# TIMESTAMP UTILITY (Fixes bug found across agents)
# =============================================================================

def get_timestamp() -> str:
    """
    Get ISO format timestamp in UTC.

    Use this instead of hardcoded "now" strings found in multiple agents.
    """
    return datetime.now(timezone.utc).isoformat()


def get_timestamp_epoch() -> float:
    """Get Unix timestamp for numeric comparisons"""
    return datetime.now(timezone.utc).timestamp()
