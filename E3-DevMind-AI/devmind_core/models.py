"""
Core data models for E3 DevMind AI
All models use Pydantic for validation and serialization
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class AgentRole(str, Enum):
    """Agent roles in the system"""
    COMMAND = "command"
    STRATEGIC = "strategic"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    KNOWLEDGE = "knowledge"
    PROJECT_MGMT = "project_management"
    MARKET = "market"


class AgentCapability(str, Enum):
    """Standard agent capabilities"""
    PREDICTION = "prediction"
    REASONING = "reasoning"
    DESIGN = "design"
    OPTIMIZATION = "optimization"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    REVIEW = "review"
    TESTING = "testing"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    INTEGRATION = "integration"
    RELIABILITY = "reliability"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    QUERY = "query"
    LEARNING = "learning"
    COORDINATION = "coordination"
    TRACKING = "tracking"
    PRIORITIZATION = "prioritization"
    MARKET_ANALYSIS = "market_analysis"
    GROWTH = "growth"


class AgentMetadata(BaseModel):
    """Metadata for each agent in the system"""
    model_config = ConfigDict(use_enum_values=True)

    agent_id: str
    agent_name: str
    role: AgentRole
    capabilities: List[AgentCapability]
    description: str
    tier: int = Field(ge=1, le=7)
    dependencies: List[str] = Field(default_factory=list)
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300


class CSDLFormat(BaseModel):
    """CSDL-formatted data structure"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    content: Dict[str, Any]
    compression_level: str = "structured"  # or "embedding"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tokens_saved: Optional[int] = None
    compression_ratio: Optional[float] = None


class QueryRequest(BaseModel):
    """Request for the E3 DevMind AI system"""
    query: str
    context: Optional[Dict[str, Any]] = None
    multimodal_data: Optional[Dict[str, Any]] = None  # voice, image, video
    requested_agents: Optional[List[str]] = None
    priority: str = "normal"  # low, normal, high, urgent
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    """Response from the E3 DevMind AI system"""
    query_id: str
    response: str
    csdl_data: Optional[CSDLFormat] = None
    agents_involved: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class KnowledgeEntry(BaseModel):
    """Entry in the E3 knowledge base"""
    entry_id: str
    title: str
    content: str
    content_type: str  # pdf, docx, image, video, code, etc.
    source: str
    tags: List[str] = Field(default_factory=list)
    category: str
    embedding: Optional[List[float]] = None
    csdl_representation: Optional[CSDLFormat] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceInput(BaseModel):
    """Voice input data"""
    audio_file_path: str
    language: str = "en"
    expected_speakers: Optional[int] = None
    is_meeting: bool = False


class VoiceOutput(BaseModel):
    """Voice output data"""
    transcript: str
    csdl: CSDLFormat
    duration_seconds: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VisionInput(BaseModel):
    """Vision input data"""
    image_path: str
    query: str
    image_type: str = "general"  # screenshot, diagram, whiteboard, design, code, error
    detail_level: str = "high"  # low, high


class VisionOutput(BaseModel):
    """Vision output data"""
    analysis: str
    csdl: CSDLFormat
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoInput(BaseModel):
    """Video input data"""
    video_path: str
    video_type: str = "general"  # meeting, demo, tutorial
    frame_interval_seconds: int = 30
    max_frames: int = 20


class VideoOutput(BaseModel):
    """Video output data"""
    transcript: Optional[VoiceOutput] = None
    visual_moments: List[VisionOutput] = Field(default_factory=list)
    summary: str
    csdl: CSDLFormat
    duration_seconds: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectMetrics(BaseModel):
    """E3 project metrics"""
    project_id: str
    project_name: str
    active_tasks: int = 0
    completed_tasks: int = 0
    blocked_tasks: int = 0
    team_velocity: float = 0.0
    code_churn_rate: float = 0.0
    defect_rate: float = 0.0
    test_coverage: float = 0.0
    build_success_rate: float = 1.0
    deployment_frequency: float = 0.0
    updated_at: datetime = Field(default_factory=datetime.now)


class RiskPrediction(BaseModel):
    """Risk prediction from Prophet agent"""
    risk_id: str
    risk_type: str  # timeline, quality, resource, security, technical
    description: str
    probability: float = Field(ge=0.0, le=1.0)
    impact: str  # low, medium, high, critical
    predicted_date: Optional[datetime] = None
    mitigation_suggestions: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    related_metrics: Dict[str, Any] = Field(default_factory=dict)


class AgentTaskStatus(str, Enum):
    """Status of agent tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask(BaseModel):
    """Task assigned to an agent"""
    model_config = ConfigDict(use_enum_values=True)

    task_id: str
    agent_id: str
    task_type: str
    input_data: Dict[str, Any]
    status: AgentTaskStatus = AgentTaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None


class SystemHealth(BaseModel):
    """Overall system health status"""
    status: str  # healthy, degraded, unhealthy
    csdl_vllm_status: str
    qdrant_status: str
    postgres_status: str
    redis_status: str
    active_agents: int
    total_agents: int
    current_load: float = Field(ge=0.0, le=1.0)
    avg_response_time_ms: float
    errors_last_hour: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class IntegrationConfig(BaseModel):
    """Configuration for external integrations"""
    integration_name: str  # github, gitlab, slack, jira, etc.
    enabled: bool = True
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)


class E3Document(BaseModel):
    """E3 document metadata"""
    document_id: str
    filename: str
    file_path: str
    file_type: str  # pdf, docx, xlsx, pptx, image, video, etc.
    file_size_bytes: int
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.now)
    processed: bool = False
    processing_status: str = "pending"  # pending, processing, completed, failed
    extracted_text: Optional[str] = None
    extracted_images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    knowledge_entries: List[str] = Field(default_factory=list)  # IDs of created entries
    metadata: Dict[str, Any] = Field(default_factory=dict)
