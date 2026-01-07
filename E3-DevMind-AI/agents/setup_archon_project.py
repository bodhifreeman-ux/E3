#!/usr/bin/env python3
"""
E3 DevMind Archon Project Setup

Creates the E3 DevMind project in Archon with:
- Project metadata
- Initial tasks for each agent tier
- Documentation links

Run this script after starting Archon services to initialize the project.

Usage:
    python3 -m agents.setup_archon_project
"""

import asyncio
import sys
sys.path.insert(0, '/home/bodhifreeman/E3/E3-DevMind-AI')

from datetime import datetime, timezone
from agents.archon_integration import ArchonBridge, ArchonConfig


# E3 DevMind Project Definition
E3_PROJECT = {
    "title": "E3 DevMind AI Agent Swarm",
    "description": """
E3 DevMind is a 32-agent AI development swarm with CSDL (Context-Semantic Dynamic Language) compression.

## Architecture
- **Tier 7 (Orchestration)**: Conductor - Supreme orchestrator
- **Tier 6 (Intelligence)**: Oracle - Central intelligence router
- **Tier 5 (Leadership)**: Strategist, Synthesizer, Sage - Strategic leadership
- **Tier 4 (Specialists)**: 27 specialized agents across domains

## Key Features
- CSDL-ANLT compression (85-98% token reduction)
- Inter-agent collaboration with circuit breaker pattern
- Capability discovery and intelligent routing
- Request deduplication with TTL cache
- State-of-the-art system contexts for all agents

## Components
- **CSDL-ANLT**: Binary compression, semantic deduplication, delta encoding
- **CSDL-14B**: Fine-tuned 14B model for CSDL understanding
- **Message Bus**: Async inter-agent communication
- **Archon Integration**: Knowledge base and task management

## Repository
https://github.com/bodhifreeman/E3
""",
    "github_repo": "https://github.com/bodhifreeman/E3"
}


# Initial Tasks by Category
INITIAL_TASKS = [
    # Core System
    {
        "title": "Initialize CSDL-14B Model Server",
        "description": "Start the CSDL-14B inference server for agent processing",
        "status": "done",
        "assignee": "User"
    },
    {
        "title": "Configure CSDL-ANLT Compression",
        "description": "Set up semantic compression pipeline with binary encoding and delta compression",
        "status": "done",
        "assignee": "User"
    },
    {
        "title": "Implement Agent Collaboration Framework",
        "description": "Add circuit breaker, retry logic, capability discovery across all 32 agents",
        "status": "done",
        "assignee": "Archon"
    },
    {
        "title": "Create State-of-the-Art System Contexts",
        "description": "Define reasoning frameworks, quality standards, and collaboration protocols for all agents",
        "status": "done",
        "assignee": "Archon"
    },

    # Archon Integration
    {
        "title": "Clone and Integrate Archon MCP Server",
        "description": "Set up Archon for knowledge base and task management",
        "status": "done",
        "assignee": "Archon"
    },
    {
        "title": "Create Archon Integration Bridge",
        "description": "Bridge between E3 DevMind agents and Archon MCP tools",
        "status": "done",
        "assignee": "AI IDE Agent"
    },
    {
        "title": "Add Archon Methods to Base Agent",
        "description": "Enable all agents to access Archon knowledge and task management",
        "status": "done",
        "assignee": "AI IDE Agent"
    },

    # Ongoing Tasks
    {
        "title": "Document Agent Capabilities",
        "description": "Create comprehensive documentation for all 32 agent capabilities",
        "status": "todo",
        "assignee": "AI IDE Agent"
    },
    {
        "title": "Add Knowledge Sources to Archon",
        "description": "Crawl and index relevant documentation for agent knowledge base",
        "status": "todo",
        "assignee": "User"
    },
    {
        "title": "Implement Agent Health Monitoring",
        "description": "Add real-time health dashboards for all agents",
        "status": "todo",
        "assignee": "AI IDE Agent"
    },
    {
        "title": "Create Agent Testing Suite",
        "description": "Comprehensive test coverage for agent collaboration patterns",
        "status": "todo",
        "assignee": "AI IDE Agent"
    },

    # Future Enhancements
    {
        "title": "Add Persistent Agent Memory",
        "description": "Implement long-term memory storage with CSDL compression",
        "status": "todo",
        "assignee": "Archon"
    },
    {
        "title": "Build Agent Performance Analytics",
        "description": "Track success rates, latency, and collaboration patterns",
        "status": "todo",
        "assignee": "AI IDE Agent"
    },
    {
        "title": "Create Visual Agent Graph",
        "description": "Real-time visualization of inter-agent communication",
        "status": "todo",
        "assignee": "AI IDE Agent"
    },
]


# Agent Tier Documentation
AGENT_TIERS = """
## E3 DevMind Agent Tiers

### Tier 7 - Supreme Orchestration
- **Conductor**: Supreme orchestrator for complex multi-agent operations

### Tier 6 - Central Intelligence
- **Oracle**: Central intelligence router, query distribution, response synthesis

### Tier 5 - Strategic Leadership
- **Strategist**: Long-term planning and strategic decision making
- **Synthesizer**: Information fusion and comprehensive reports
- **Sage**: Deep wisdom and historical pattern recognition

### Tier 4 - Domain Specialists

**Architecture & Design**
- Architect: System design and technical architecture
- Craftsman: Code quality and craftsmanship standards
- Artisan: UI/UX design and user experience
- Sculptor: Data modeling and schema design

**Development & Operations**
- Forge: Build systems and toolchain optimization
- Engineer: Implementation and feature development
- Scribe: Documentation and technical writing
- Chronicler: Version control and change tracking

**Quality & Security**
- Sentinel: Security scanning and vulnerability detection
- Guardian: Access control and authentication
- Inspector: Code review and quality gates
- Pathfinder: Testing strategies and coverage analysis

**Intelligence & Learning**
- Maven: Dependency management and ecosystem knowledge
- Scholar: Research and technology evaluation
- Mentor: Best practices and code education
- Catalyst: Innovation and experimental features

**Operations & Monitoring**
- Monitor: System health and performance tracking
- Navigator: Project management and task routing
- Mediator: Conflict resolution and consensus building
- Herald: Notifications and communication

**Analysis & Optimization**
- Optimizer: Performance tuning and efficiency
- Profiler: Runtime analysis and bottleneck detection
- Analyzer: Static analysis and pattern detection
- Auditor: Compliance and standards verification

**Support & Integration**
- Liaison: External API integration
- Translator: Cross-language and format conversion
- Archivist: Knowledge preservation and retrieval
"""


async def setup_e3_project():
    """Set up E3 DevMind project in Archon"""
    print("=" * 60)
    print("  E3 DevMind Archon Project Setup")
    print("=" * 60)
    print()

    # Create bridge with config
    config = ArchonConfig.from_env()
    bridge = ArchonBridge(config)

    try:
        # Check Archon health
        print("Checking Archon connectivity...")
        health = await bridge.health_check()

        if not health.success:
            print(f"ERROR: Archon not available - {health.error}")
            print("Please start Archon services first:")
            print("  ./Start-Archon-Server.desktop")
            return False

        print(f"  Archon is healthy (latency: {health.latency_ms:.0f}ms)")
        print()

        # Check for existing project
        print("Checking for existing E3 DevMind project...")
        projects = await bridge.find_projects(query="E3 DevMind")

        project_id = None

        if projects.success and projects.data:
            project_list = projects.data.get("projects", [])
            for p in project_list:
                if "E3 DevMind" in p.get("title", ""):
                    project_id = p.get("id")
                    print(f"  Found existing project: {project_id}")
                    break

        # Create project if not exists
        if not project_id:
            print("Creating E3 DevMind project...")
            result = await bridge.create_project(
                title=E3_PROJECT["title"],
                description=E3_PROJECT["description"],
                github_repo=E3_PROJECT["github_repo"]
            )

            if result.success:
                project_id = result.data.get("project", {}).get("id")
                print(f"  Created project: {project_id}")
            else:
                print(f"  ERROR: Failed to create project - {result.error}")
                return False
        else:
            print("  Project already exists, skipping creation")

        print()

        # Create initial tasks
        print("Setting up initial tasks...")
        tasks_created = 0
        tasks_skipped = 0

        for task_def in INITIAL_TASKS:
            # Check if task exists
            existing = await bridge.find_tasks(query=task_def["title"])

            if existing.success and existing.data:
                task_list = existing.data.get("tasks", [])
                if any(task_def["title"] in t.get("title", "") for t in task_list):
                    tasks_skipped += 1
                    continue

            # Create task
            result = await bridge.create_task(
                project_id=project_id,
                title=task_def["title"],
                description=task_def["description"],
                status=task_def["status"],
                assignee=task_def["assignee"]
            )

            if result.success:
                tasks_created += 1
                status_icon = "✓" if task_def["status"] == "done" else "○"
                print(f"  {status_icon} {task_def['title']}")
            else:
                print(f"  ✗ Failed: {task_def['title']} - {result.error}")

        print()
        print(f"Tasks created: {tasks_created}")
        print(f"Tasks skipped (already exist): {tasks_skipped}")
        print()

        # Create documentation document
        print("Adding agent tier documentation...")
        doc_result = await bridge.create_document(
            project_id=project_id,
            title="Agent Tier Reference",
            document_type="documentation",
            content=AGENT_TIERS
        )

        if doc_result.success:
            print("  Document created successfully")
        else:
            print(f"  Document may already exist: {doc_result.error}")

        print()
        print("=" * 60)
        print("  Setup Complete!")
        print("=" * 60)
        print()
        print("Access Archon UI at: http://localhost:3737")
        print(f"Project ID: {project_id}")
        print()

        return True

    finally:
        await bridge.close()


async def main():
    """Main entry point"""
    try:
        success = await setup_e3_project()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nSetup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
