"""
System configuration for E3 DevMind AI
Loads environment variables and provides configuration objects
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class CSDLvLLMConfig(BaseSettings):
    """Configuration for CSDL-vLLM integration"""
    url: str = Field(default="http://localhost:8002", alias="CSDL_VLLM_URL")
    api_key: Optional[str] = Field(default=None, alias="CSDL_VLLM_API_KEY")
    timeout: int = 120
    max_retries: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(
        default="postgresql://devmind:password@localhost:5432/e3_devmind",
        alias="DATABASE_URL"
    )
    pool_size: int = 20
    max_overflow: int = 10
    echo: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


class QdrantConfig(BaseSettings):
    """Qdrant vector database configuration"""
    host: str = Field(default="localhost", alias="QDRANT_HOST")
    port: int = Field(default=6333, alias="QDRANT_PORT")
    collection_name: str = "e3_knowledge"
    vector_size: int = 768  # sentence-transformers default
    distance_metric: str = "cosine"

    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisConfig(BaseSettings):
    """Redis configuration"""
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


class ANLTConfig(BaseSettings):
    """ANLT (Agent-Native Language Translation) configuration"""
    compression_level: str = Field(default="structured", alias="ANLT_COMPRESSION_LEVEL")
    enable_metrics: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


class MultimodalConfig(BaseSettings):
    """Multimodal processing configuration"""
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    default_tts_voice: str = Field(default="nova", alias="DEFAULT_TTS_VOICE")
    tts_speed: float = Field(default=1.0, alias="TTS_SPEED")
    whisper_model: str = "whisper-1"
    vision_model: str = "gpt-4-vision-preview"
    vision_detail: str = "high"
    max_video_frames: int = 30
    frame_interval_seconds: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


class IntegrationsConfig(BaseSettings):
    """External integrations configuration"""
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    gitlab_token: Optional[str] = Field(default=None, alias="GITLAB_TOKEN")
    slack_bot_token: Optional[str] = Field(default=None, alias="SLACK_BOT_TOKEN")
    jira_api_token: Optional[str] = Field(default=None, alias="JIRA_API_TOKEN")
    linear_api_key: Optional[str] = Field(default=None, alias="LINEAR_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


class E3Config(BaseSettings):
    """E3 Consortium specific configuration"""
    project_name: str = Field(default="E3 Consortium", alias="E3_PROJECT_NAME")
    knowledge_path: str = Field(default="/app/knowledge", alias="E3_KNOWLEDGE_PATH")

    class Config:
        env_file = ".env"
        case_sensitive = False


class SystemConfig(BaseSettings):
    """Overall system configuration"""
    max_concurrent_agents: int = Field(default=32, alias="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(default=300, alias="AGENT_TIMEOUT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    enable_metrics: bool = True
    enable_tracing: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


class AgentRegistryConfig:
    """Configuration for the 32 agents"""

    AGENTS: List[Dict[str, Any]] = [
        # TIER 1: COMMAND & COORDINATION
        {
            "agent_id": "oracle",
            "agent_name": "Oracle",
            "role": "command",
            "tier": 1,
            "capabilities": ["coordination", "reasoning", "synthesis"],
            "description": "Primary coordinator and swarm orchestrator"
        },

        # TIER 2: STRATEGIC INTELLIGENCE
        {
            "agent_id": "prophet",
            "agent_name": "Prophet",
            "role": "strategic",
            "tier": 2,
            "capabilities": ["prediction", "analysis"],
            "description": "Predictive analytics and risk prediction"
        },
        {
            "agent_id": "sage",
            "agent_name": "Sage",
            "role": "strategic",
            "tier": 2,
            "capabilities": ["reasoning", "optimization"],
            "description": "Meta-reasoner and process analyzer"
        },
        {
            "agent_id": "strategist",
            "agent_name": "Strategist",
            "role": "strategic",
            "tier": 2,
            "capabilities": ["design", "analysis"],
            "description": "Solution designer and strategic planner"
        },
        {
            "agent_id": "economist",
            "agent_name": "Economist",
            "role": "strategic",
            "tier": 2,
            "capabilities": ["optimization", "analysis"],
            "description": "Resource optimizer and ROI analyst"
        },

        # TIER 3: DEEP ANALYSIS
        {
            "agent_id": "investigator",
            "agent_name": "Investigator",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["analysis", "reasoning"],
            "description": "Technical analyzer and problem decomposition"
        },
        {
            "agent_id": "critic",
            "agent_name": "Critic",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["review", "analysis"],
            "description": "Devil's advocate and quality assurance"
        },
        {
            "agent_id": "visionary",
            "agent_name": "Visionary",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["design", "reasoning"],
            "description": "Innovation engine and creative problem-solving"
        },
        {
            "agent_id": "detective",
            "agent_name": "Detective",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["analysis", "reasoning"],
            "description": "Pattern recognition and correlation analysis"
        },
        {
            "agent_id": "historian",
            "agent_name": "Historian",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["query", "analysis"],
            "description": "Institutional memory and context provider"
        },
        {
            "agent_id": "cartographer",
            "agent_name": "Cartographer",
            "role": "analysis",
            "tier": 3,
            "capabilities": ["analysis", "synthesis"],
            "description": "Knowledge mapper and structure optimizer"
        },

        # TIER 4: EXECUTION SPECIALISTS
        {
            "agent_id": "architect",
            "agent_name": "Architect",
            "role": "execution",
            "tier": 4,
            "capabilities": ["design", "analysis"],
            "description": "System designer and architecture expert"
        },
        {
            "agent_id": "forge",
            "agent_name": "Forge",
            "role": "execution",
            "tier": 4,
            "capabilities": ["generation"],
            "description": "Code generator and implementation expert"
        },
        {
            "agent_id": "craftsman",
            "agent_name": "Craftsman",
            "role": "execution",
            "tier": 4,
            "capabilities": ["review", "analysis"],
            "description": "Code quality and review expert"
        },
        {
            "agent_id": "scientist",
            "agent_name": "Scientist",
            "role": "execution",
            "tier": 4,
            "capabilities": ["testing", "analysis"],
            "description": "Testing strategy and validation expert"
        },
        {
            "agent_id": "sentinel",
            "agent_name": "Sentinel",
            "role": "execution",
            "tier": 4,
            "capabilities": ["security", "analysis"],
            "description": "Security guardian and threat detection"
        },
        {
            "agent_id": "ops",
            "agent_name": "Ops",
            "role": "execution",
            "tier": 4,
            "capabilities": ["deployment", "optimization"],
            "description": "DevOps and infrastructure expert"
        },
        {
            "agent_id": "optimizer",
            "agent_name": "Optimizer",
            "role": "execution",
            "tier": 4,
            "capabilities": ["performance", "optimization"],
            "description": "Performance engineer and optimization expert"
        },
        {
            "agent_id": "documenter",
            "agent_name": "Documenter",
            "role": "execution",
            "tier": 4,
            "capabilities": ["documentation", "generation"],
            "description": "Documentation and knowledge capture expert"
        },
        {
            "agent_id": "integrator",
            "agent_name": "Integrator",
            "role": "execution",
            "tier": 4,
            "capabilities": ["integration", "design"],
            "description": "Systems integration and API design expert"
        },
        {
            "agent_id": "guardian",
            "agent_name": "Guardian",
            "role": "execution",
            "tier": 4,
            "capabilities": ["reliability", "analysis"],
            "description": "Reliability engineer and resilience expert"
        },

        # TIER 5: E3 KNOWLEDGE MASTERY
        {
            "agent_id": "librarian",
            "agent_name": "Librarian",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["analysis", "generation"],
            "description": "Document processor and ingestion expert"
        },
        {
            "agent_id": "curator",
            "agent_name": "Curator",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["analysis", "optimization"],
            "description": "Knowledge organizer and structure expert"
        },
        {
            "agent_id": "scholar",
            "agent_name": "Scholar",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["research", "analysis"],
            "description": "Deep researcher and external intelligence"
        },
        {
            "agent_id": "synthesizer",
            "agent_name": "Synthesizer",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["synthesis", "reasoning"],
            "description": "Insight generator and multi-source synthesizer"
        },
        {
            "agent_id": "oracle_kb",
            "agent_name": "Oracle KB",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["query", "analysis"],
            "description": "Knowledge base query and instant answers"
        },
        {
            "agent_id": "learner",
            "agent_name": "Learner",
            "role": "knowledge",
            "tier": 5,
            "capabilities": ["learning", "optimization"],
            "description": "Continuous improvement and learning expert"
        },

        # TIER 6: PROJECT MANAGEMENT
        {
            "agent_id": "conductor",
            "agent_name": "Conductor",
            "role": "project_mgmt",
            "tier": 6,
            "capabilities": ["coordination", "analysis"],
            "description": "Project orchestrator and workstream manager"
        },
        {
            "agent_id": "tracker",
            "agent_name": "Tracker",
            "role": "project_mgmt",
            "tier": 6,
            "capabilities": ["tracking", "analysis"],
            "description": "Progress monitor and status tracker"
        },
        {
            "agent_id": "prioritizer",
            "agent_name": "Prioritizer",
            "role": "project_mgmt",
            "tier": 6,
            "capabilities": ["prioritization", "analysis"],
            "description": "Task optimizer and priority manager"
        },

        # TIER 7: MARKET & GROWTH
        {
            "agent_id": "navigator",
            "agent_name": "Navigator",
            "role": "market",
            "tier": 7,
            "capabilities": ["market_analysis", "research"],
            "description": "Market intelligence and competitive analyst"
        },
        {
            "agent_id": "catalyst",
            "agent_name": "Catalyst",
            "role": "market",
            "tier": 7,
            "capabilities": ["growth", "analysis"],
            "description": "Growth strategy and expansion expert"
        },
    ]


@lru_cache()
def get_config() -> Dict[str, Any]:
    """
    Get complete system configuration
    Cached for performance
    """
    return {
        "csdl_vllm": CSDLvLLMConfig(),
        "database": DatabaseConfig(),
        "qdrant": QdrantConfig(),
        "redis": RedisConfig(),
        "anlt": ANLTConfig(),
        "multimodal": MultimodalConfig(),
        "integrations": IntegrationsConfig(),
        "e3": E3Config(),
        "system": SystemConfig(),
        "agents": AgentRegistryConfig.AGENTS
    }


def get_agent_config(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific agent"""
    for agent in AgentRegistryConfig.AGENTS:
        if agent["agent_id"] == agent_id:
            return agent
    return None


def get_agents_by_tier(tier: int) -> List[Dict[str, Any]]:
    """Get all agents in a specific tier"""
    return [agent for agent in AgentRegistryConfig.AGENTS if agent["tier"] == tier]


def get_agents_by_role(role: str) -> List[Dict[str, Any]]:
    """Get all agents with a specific role"""
    return [agent for agent in AgentRegistryConfig.AGENTS if agent["role"] == role]
