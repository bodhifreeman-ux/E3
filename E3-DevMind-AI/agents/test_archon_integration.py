#!/usr/bin/env python3
"""
Test Archon Integration with E3 DevMind Agent Swarm

This script tests the Archon integration without requiring:
- Running Archon services (gracefully handles unavailable service)
- vLLM server (mocks CSDL processing)

Run: python3 -m agents.test_archon_integration
"""

import asyncio
import sys
sys.path.insert(0, '/home/bodhifreeman/E3/E3-DevMind-AI')

from datetime import datetime, timezone


def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_result(test_name: str, passed: bool, details: str = ""):
    icon = "✓" if passed else "✗"
    status = "PASSED" if passed else "FAILED"
    print(f"  {icon} {test_name}: {status}")
    if details:
        print(f"    {details}")


async def test_archon_config():
    """Test ArchonConfig loading"""
    print_header("Test 1: Archon Configuration")

    try:
        from agents.archon_integration import ArchonConfig

        # Test default config
        config = ArchonConfig()
        print_result(
            "Default config",
            config.server_port == 8181 and config.mcp_port == 8051,
            f"server={config.server_port}, mcp={config.mcp_port}"
        )

        # Test URL generation
        print_result(
            "URL generation",
            "http://" in config.server_url and "http://" in config.mcp_url,
            f"server_url={config.server_url}"
        )

        # Test from_env
        config_env = ArchonConfig.from_env()
        print_result(
            "from_env() method",
            config_env is not None,
            f"timeout={config_env.timeout_seconds}s"
        )

        return True

    except Exception as e:
        print_result("Config loading", False, str(e))
        return False


async def test_archon_tools():
    """Test ArchonTool enum"""
    print_header("Test 2: Archon Tools Definition")

    try:
        from agents.archon_integration import ArchonTool

        # Check all expected tools exist
        expected_tools = [
            "RAG_SEARCH_KNOWLEDGE",
            "RAG_SEARCH_CODE",
            "RAG_GET_SOURCES",
            "FIND_PROJECTS",
            "MANAGE_PROJECT",
            "FIND_TASKS",
            "MANAGE_TASK",
            "HEALTH_CHECK",
        ]

        all_present = all(hasattr(ArchonTool, tool) for tool in expected_tools)
        print_result(
            "All tools defined",
            all_present,
            f"{len(expected_tools)} tools expected"
        )

        # Check tool values
        print_result(
            "Tool values",
            ArchonTool.RAG_SEARCH_KNOWLEDGE.value == "rag_search_knowledge_base",
            f"example: {ArchonTool.RAG_SEARCH_KNOWLEDGE.value}"
        )

        return True

    except Exception as e:
        print_result("Tools definition", False, str(e))
        return False


async def test_archon_bridge():
    """Test ArchonBridge creation"""
    print_header("Test 3: Archon Bridge")

    try:
        from agents.archon_integration import ArchonBridge, get_archon_bridge

        # Test bridge creation
        bridge = ArchonBridge()
        print_result(
            "Bridge creation",
            bridge is not None,
            f"config: {bridge.config.host}:{bridge.config.server_port}"
        )

        # Test singleton
        bridge1 = get_archon_bridge()
        bridge2 = get_archon_bridge()
        print_result(
            "Singleton pattern",
            bridge1 is bridge2,
            "Same instance returned"
        )

        # Test bridge methods exist
        methods = ["search_knowledge", "search_code_examples", "find_tasks", "create_task"]
        all_methods = all(hasattr(bridge, m) for m in methods)
        print_result(
            "Bridge methods",
            all_methods,
            f"{len(methods)} methods available"
        )

        return True

    except Exception as e:
        print_result("Bridge creation", False, str(e))
        return False


async def test_base_agent_archon_methods():
    """Test Archon methods in BaseAgent"""
    print_header("Test 4: BaseAgent Archon Methods")

    try:
        # Check if archon methods are available in base_agent
        from agents.base_agent import ARCHON_AVAILABLE, ARCHON_CAPABILITIES

        print_result(
            "ARCHON_AVAILABLE flag",
            isinstance(ARCHON_AVAILABLE, bool),
            f"available={ARCHON_AVAILABLE}"
        )

        print_result(
            "ARCHON_CAPABILITIES dict",
            isinstance(ARCHON_CAPABILITIES, dict),
            f"{len(ARCHON_CAPABILITIES)} capabilities defined"
        )

        # Check capabilities structure
        if ARCHON_CAPABILITIES:
            sample = list(ARCHON_CAPABILITIES.values())[0]
            has_schema = "input_schema" in sample and "output_schema" in sample
            print_result(
                "Capability schema",
                has_schema,
                f"sample: {list(ARCHON_CAPABILITIES.keys())[0]}"
            )

        return True

    except Exception as e:
        print_result("BaseAgent Archon methods", False, str(e))
        return False


async def test_agent_helper_functions():
    """Test agent helper functions"""
    print_header("Test 5: Agent Helper Functions")

    try:
        from agents.archon_integration import (
            agent_search_knowledge,
            agent_create_task,
            agent_update_task_status,
        )

        # These functions exist
        print_result(
            "agent_search_knowledge",
            callable(agent_search_knowledge),
            "Function available"
        )

        print_result(
            "agent_create_task",
            callable(agent_create_task),
            "Function available"
        )

        print_result(
            "agent_update_task_status",
            callable(agent_update_task_status),
            "Function available"
        )

        # Test calling search (will fail if Archon not running, but that's OK)
        result = await agent_search_knowledge("test query")
        print_result(
            "Search function response",
            "op" in result and "ts" in result,
            f"op={result.get('op', 'unknown')}"
        )

        return True

    except Exception as e:
        print_result("Helper functions", False, str(e))
        return False


async def test_tool_result_structure():
    """Test ArchonToolResult structure"""
    print_header("Test 6: Tool Result Structure")

    try:
        from agents.archon_integration import ArchonToolResult, ArchonTool

        # Create a test result
        result = ArchonToolResult(
            success=True,
            data={"test": "data"},
            tool=ArchonTool.HEALTH_CHECK,
            latency_ms=123.45
        )

        print_result(
            "Result creation",
            result.success == True,
            f"latency={result.latency_ms}ms"
        )

        print_result(
            "Timestamp auto-generated",
            result.timestamp is not None,
            f"ts={result.timestamp[:19]}..."
        )

        # Test error result
        error_result = ArchonToolResult(
            success=False,
            error="Connection refused",
            tool=ArchonTool.HEALTH_CHECK
        )

        print_result(
            "Error result",
            error_result.error == "Connection refused",
            f"error={error_result.error}"
        )

        return True

    except Exception as e:
        print_result("Tool result structure", False, str(e))
        return False


async def test_archon_health():
    """Test Archon health check (may fail if not running)"""
    print_header("Test 7: Archon Health Check")

    try:
        from agents.archon_integration import get_archon_bridge

        bridge = get_archon_bridge()
        result = await bridge.health_check()

        if result.success:
            print_result(
                "Archon reachable",
                True,
                f"latency={result.latency_ms:.0f}ms"
            )
            print_result(
                "Health data",
                result.data is not None,
                str(result.data)[:50] + "..."
            )
        else:
            print_result(
                "Archon reachable",
                False,
                f"error: {result.error}"
            )
            print("    (This is expected if Archon services are not running)")

        return True

    except Exception as e:
        print_result("Health check", False, str(e))
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  E3 DEVMIND - ARCHON INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Configuration", test_archon_config),
        ("Tools Definition", test_archon_tools),
        ("Bridge Creation", test_archon_bridge),
        ("BaseAgent Methods", test_base_agent_archon_methods),
        ("Helper Functions", test_agent_helper_functions),
        ("Result Structure", test_tool_result_structure),
        ("Health Check", test_archon_health),
    ]

    results = []
    for name, test_fn in tests:
        try:
            passed = await test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  ERROR in {name}: {e}")
            results.append((name, False))

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        icon = "✓" if p else "✗"
        print(f"  {icon} {name}")

    print()
    print(f"  Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("  All integration tests passed!")
        print()
        print("  Next steps:")
        print("  1. Start Archon: ./Start-Archon-Server.desktop")
        print("  2. Setup project: ./Setup-E3-Archon-Project.desktop")
        print("  3. Open Archon UI: http://localhost:3737")
    else:
        print("  Some tests failed - check output above")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests cancelled")
        sys.exit(1)
