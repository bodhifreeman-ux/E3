#!/usr/bin/env python3
"""
Demonstration of the Agent Collaboration Framework

E3 DevMind Infrastructure (2026):
- CSDL Server (port 5000): CSDL-14B inference with PyTorch/CUDA
- Archon (port 8181/8051): Knowledge base, RAG, task management
- Message Bus: Async pub/sub for inter-agent communication
- CSDL-ANLT: 85-98% compression layer

This script showcases the key improvements across all 32 agents:
1. Circuit Breaker pattern - prevents cascading failures
2. Retry with Exponential Backoff - handles transient errors
3. Capability Discovery - intelligent agent routing
4. Request Deduplication - avoids redundant work
5. Timestamp utilities - fixes bugs across agents

Run: python -m agents.demo_collaboration
"""

import asyncio
import sys
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, '/home/bodhifreeman/E3/E3/E3-DevMind-AI')

from agents.collaboration import (
    # Error handling
    ErrorType,
    AgentError,

    # Circuit Breaker
    CircuitBreaker,
    CircuitBreakerState,

    # Retry logic
    RetryConfig,
    retry_with_backoff,

    # Capability Discovery
    AgentCapability,
    AgentRegistry,
    CapabilityDiscoveryService,

    # Request Deduplication
    RequestDeduplicator,

    # Main coordinator
    CollaborationCoordinator,
    get_coordinator,

    # Timestamp utilities
    get_timestamp,
    get_timestamp_epoch,
)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_subheader(text: str):
    """Print formatted subheader"""
    print(f"\n--- {text} ---")


async def demo_circuit_breaker():
    """Demonstrate circuit breaker pattern"""
    print_header("CIRCUIT BREAKER DEMO")

    cb = CircuitBreaker(
        name="test_agent",
        failure_threshold=3,
        reset_timeout_seconds=5
    )

    print(f"\nInitial state: {cb.state.value}")
    print(f"Can execute: {cb.can_execute()}")

    # Simulate failures
    print_subheader("Simulating 3 failures")
    for i in range(3):
        cb.record_failure()
        print(f"  Failure {i+1}: state={cb.state.value}, failures={cb.failure_count}")

    print(f"\nCircuit is now: {cb.state.value}")
    print(f"Can execute: {cb.can_execute()}")

    # Wait for reset
    print_subheader("Waiting 5 seconds for reset timeout...")
    await asyncio.sleep(5)

    print(f"After timeout: can_execute={cb.can_execute()}")
    print(f"State: {cb.state.value}")

    # Record success to close circuit
    cb.record_success()
    print(f"After success: state={cb.state.value}")

    print_subheader("Circuit Breaker Statistics")
    stats = cb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def demo_retry_logic():
    """Demonstrate retry with exponential backoff"""
    print_header("RETRY WITH EXPONENTIAL BACKOFF")

    config = RetryConfig(
        max_retries=3,
        initial_delay_seconds=0.5,
        exponential_base=2.0,
        jitter=False  # Disable jitter for predictable demo
    )

    # Show delay progression
    print_subheader("Backoff delay progression")
    for attempt in range(config.max_retries + 1):
        delay = config.get_delay(attempt)
        print(f"  Attempt {attempt}: delay = {delay:.2f}s")

    # Demo successful retry
    print_subheader("Retry succeeding on 3rd attempt")
    attempt_count = [0]

    async def flaky_operation():
        attempt_count[0] += 1
        print(f"    Attempt {attempt_count[0]}...")
        if attempt_count[0] < 3:
            raise ConnectionError("Transient error")
        return {"result": "success", "attempts": attempt_count[0]}

    try:
        result = await retry_with_backoff(flaky_operation, config)
        print(f"  Result: {result}")
    except AgentError as e:
        print(f"  Failed: {e.message}")


async def demo_capability_discovery():
    """Demonstrate agent capability discovery and routing"""
    print_header("CAPABILITY DISCOVERY")

    service = CapabilityDiscoveryService()

    # Register some agents
    print_subheader("Registering agents with capabilities")

    agents = [
        AgentRegistry(
            agent_id="architect",
            agent_name="Architect",
            tier=4,
            capabilities=[
                AgentCapability(
                    name="system_design",
                    version="1.0.0",
                    description="Design system architecture",
                    input_schema={"requirements": "object"},
                    output_schema={"design": "object"},
                    success_rate=0.95,
                    avg_latency_ms=2000
                ),
                AgentCapability(
                    name="code_review",
                    version="1.0.0",
                    description="Review code for patterns",
                    input_schema={"code": "string"},
                    output_schema={"issues": "array"},
                    success_rate=0.92,
                    avg_latency_ms=1500
                )
            ]
        ),
        AgentRegistry(
            agent_id="craftsman",
            agent_name="Craftsman",
            tier=4,
            capabilities=[
                AgentCapability(
                    name="code_review",
                    version="2.0.0",
                    description="Detailed code review",
                    input_schema={"code": "string"},
                    output_schema={"issues": "array"},
                    success_rate=0.98,
                    avg_latency_ms=3000
                )
            ]
        ),
        AgentRegistry(
            agent_id="sentinel",
            agent_name="Sentinel",
            tier=4,
            capabilities=[
                AgentCapability(
                    name="security_scan",
                    version="1.0.0",
                    description="Security vulnerability scan",
                    input_schema={"code": "string"},
                    output_schema={"vulnerabilities": "array"},
                    success_rate=0.99,
                    avg_latency_ms=4000
                )
            ]
        )
    ]

    for agent in agents:
        service.register_agent(agent)
        caps = [c.name for c in agent.capabilities]
        print(f"  Registered {agent.agent_name}: {caps}")

    # Find agents by capability
    print_subheader("Finding agents for 'code_review' capability")
    reviewers = service.find_agents_for_capability("code_review")
    for r in reviewers:
        cap = r.get_capability("code_review")
        print(f"  {r.agent_name}: success_rate={cap.success_rate}, latency={cap.avg_latency_ms}ms")

    # Best agent for task
    print_subheader("Finding best agent for ['code_review', 'security_scan']")
    best = service.get_best_agent_for_task(["code_review", "security_scan"])
    print(f"  Best agent: {best or 'None found (no agent has both)'}")


async def demo_request_deduplication():
    """Demonstrate request deduplication"""
    print_header("REQUEST DEDUPLICATION")

    dedup = RequestDeduplicator(ttl_seconds=10)

    request = {
        "query_type": "analyze_code",
        "code": "def hello(): pass",
        "options": {"strict": True}
    }

    # First request - cache miss
    print_subheader("First request (cache miss)")
    cached = await dedup.get_cached(request)
    print(f"  Cached result: {cached}")

    # Store result
    result = {"analysis": "OK", "score": 0.95}
    await dedup.cache_result(request, result)
    print(f"  Cached: {result}")

    # Second request - cache hit
    print_subheader("Second identical request (cache hit)")
    cached = await dedup.get_cached(request)
    print(f"  Cached result: {cached}")

    # Different request - cache miss
    print_subheader("Different request (cache miss)")
    different_request = {**request, "options": {"strict": False}}
    cached = await dedup.get_cached(different_request)
    print(f"  Cached result: {cached}")


async def demo_timestamp_utilities():
    """Demonstrate timestamp utilities (fixes bug)"""
    print_header("TIMESTAMP UTILITIES (Bug Fix)")

    print_subheader("Old buggy pattern (found in multiple agents)")
    buggy = {"timestamp": "now"}  # This was actual code!
    print(f"  Buggy: {buggy}")

    print_subheader("Fixed pattern using utilities")
    fixed = {
        "timestamp": get_timestamp(),
        "timestamp_epoch": get_timestamp_epoch()
    }
    print(f"  ISO: {fixed['timestamp']}")
    print(f"  Epoch: {fixed['timestamp_epoch']}")


async def demo_full_coordinator():
    """Demonstrate the full collaboration coordinator"""
    print_header("FULL COLLABORATION COORDINATOR")

    coordinator = get_coordinator()

    # Register capabilities
    print_subheader("Setting up agents")

    coordinator.capability_service.register_agent(
        AgentRegistry(
            agent_id="oracle",
            agent_name="Oracle",
            tier=6,
            capabilities=[
                AgentCapability(
                    name="knowledge_query",
                    version="1.0.0",
                    description="Query knowledge base",
                    input_schema={},
                    output_schema={},
                    success_rate=0.95
                )
            ]
        )
    )
    print("  Registered Oracle with 'knowledge_query' capability")

    # Show circuit breaker stats
    print_subheader("Circuit breaker statistics")
    stats = coordinator.get_all_circuit_stats()
    if stats:
        for s in stats:
            print(f"  {s['name']}: state={s['state']}, success_rate={s['success_rate']}")
    else:
        print("  No circuit breakers active yet")


async def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  E3 DEVMIND AGENT COLLABORATION FRAMEWORK DEMO")
    print("  Showcasing improvements from 6-agent analysis")
    print("=" * 60)

    await demo_circuit_breaker()
    await demo_retry_logic()
    await demo_capability_discovery()
    await demo_request_deduplication()
    await demo_timestamp_utilities()
    await demo_full_coordinator()

    print_header("DEMO COMPLETE")
    print("""
Key improvements implemented:

1. CIRCUIT BREAKER
   - Prevents cascading failures
   - Auto-recovers after timeout
   - Tracks success/failure rates

2. RETRY WITH EXPONENTIAL BACKOFF
   - Handles transient errors gracefully
   - Configurable delays and attempts
   - Jitter option to prevent thundering herd

3. CAPABILITY DISCOVERY
   - Agents declare their capabilities
   - Intelligent routing to best agent
   - Fallback to alternatives on failure

4. REQUEST DEDUPLICATION
   - Avoids redundant processing
   - TTL-based cache invalidation
   - Semantic request hashing

5. TIMESTAMP UTILITIES
   - Fixes "now" string bugs across agents
   - Provides ISO and epoch formats
   - UTC timezone aware

These patterns were identified as the #1 improvement
across ALL 32 E3 DevMind agents by 6 parallel analysis agents.
""")


if __name__ == "__main__":
    asyncio.run(main())
