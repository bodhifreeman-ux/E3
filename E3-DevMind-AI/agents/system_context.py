"""
State-of-the-Art Agent System Context Framework

This module provides the modern system context structure for all 32 E3 DevMind agents.
Based on 2025-2026 best practices identified through comprehensive analysis.

Key Components:
1. Behavioral Instructions - HOW to perform tasks
2. Reasoning Frameworks - Chain-of-thought patterns
3. Quality Standards - Output constraints and validation
4. Collaboration Protocols - Inter-agent communication rules
5. Error Handling - Graceful degradation strategies
6. Confidence Calibration - Uncertainty quantification

Every agent should use build_system_context() to create their context.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class AgentTier(Enum):
    """Agent hierarchy tiers"""
    TIER_6_ORCHESTRATION = 6  # Oracle, Conductor
    TIER_5_STRATEGIC = 5      # Visionary, Prophet, Navigator
    TIER_4_SPECIALIST = 4     # Most agents
    TIER_3_SUPPORT = 3        # Simple support agents


class ReasoningMode(Enum):
    """Reasoning approaches for different task types"""
    ANALYTICAL = "analytical"      # Step-by-step logical analysis
    CREATIVE = "creative"          # Exploratory, divergent thinking
    CRITICAL = "critical"          # Evaluation, finding flaws
    SYNTHETIC = "synthetic"        # Combining multiple inputs
    INVESTIGATIVE = "investigative"  # Root cause, deep dive


@dataclass
class QualityStandards:
    """Quality standards for agent outputs"""
    min_confidence_threshold: float = 0.7
    require_evidence: bool = True
    require_reasoning_chain: bool = True
    max_assumptions_allowed: int = 3
    require_alternatives: bool = False
    output_validation: bool = True


@dataclass
class CollaborationProtocol:
    """Inter-agent collaboration rules"""
    can_request_help: bool = True
    preferred_collaborators: List[str] = field(default_factory=list)
    escalation_path: List[str] = field(default_factory=list)
    max_collaboration_depth: int = 3
    timeout_seconds: float = 30.0


@dataclass
class ErrorHandling:
    """Error handling strategies"""
    on_uncertainty: str = "state_confidence_and_proceed"
    on_missing_context: str = "request_clarification"
    on_conflicting_inputs: str = "present_alternatives"
    on_capability_exceeded: str = "escalate_to_oracle"
    fallback_response: bool = True


@dataclass
class TemperatureProfile:
    """Context-aware temperature settings"""
    deterministic_tasks: float = 0.1    # Code gen, validation
    analytical_tasks: float = 0.2       # Analysis, review
    planning_tasks: float = 0.3         # Architecture, strategy
    creative_tasks: float = 0.5         # Brainstorming, exploration
    default: float = 0.3


# =============================================================================
# REASONING FRAMEWORKS
# =============================================================================

REASONING_FRAMEWORKS = {
    "chain_of_thought": {
        "description": "Step-by-step logical reasoning",
        "steps": [
            "1. Understand the request and context",
            "2. Identify key constraints and requirements",
            "3. Break down into sub-problems",
            "4. Analyze each sub-problem systematically",
            "5. Synthesize findings into coherent response",
            "6. Validate against requirements",
            "7. State confidence and caveats"
        ]
    },
    "tree_of_thought": {
        "description": "Explore multiple solution branches",
        "steps": [
            "1. Generate multiple initial approaches",
            "2. Evaluate each approach against criteria",
            "3. Prune unpromising branches",
            "4. Deep-dive promising branches",
            "5. Compare final candidates",
            "6. Select best with justification"
        ]
    },
    "critical_analysis": {
        "description": "Find flaws and weaknesses",
        "steps": [
            "1. Identify claims and assumptions",
            "2. Check logical consistency",
            "3. Find edge cases and failure modes",
            "4. Evaluate evidence quality",
            "5. Identify what could go wrong",
            "6. Suggest improvements"
        ]
    },
    "investigative": {
        "description": "Deep root cause analysis",
        "steps": [
            "1. Gather all available evidence",
            "2. Form initial hypotheses",
            "3. Test hypotheses against evidence",
            "4. Eliminate unlikely causes",
            "5. Identify root cause",
            "6. Validate with additional checks"
        ]
    },
    "synthesis": {
        "description": "Combine multiple inputs coherently",
        "steps": [
            "1. Identify all input sources",
            "2. Extract key points from each",
            "3. Find agreements and conflicts",
            "4. Resolve conflicts with reasoning",
            "5. Weave into unified narrative",
            "6. Ensure nothing important is lost"
        ]
    }
}


# =============================================================================
# BEHAVIORAL GUIDELINES
# =============================================================================

BEHAVIORAL_GUIDELINES = {
    "communication": [
        "Communicate ONLY in CSDL - never natural language",
        "Include confidence scores on all outputs",
        "State assumptions explicitly",
        "Provide reasoning chains, not just conclusions",
        "Flag areas of uncertainty"
    ],
    "quality": [
        "Prefer explicit over implicit",
        "Fail fast rather than silently degrade",
        "Validate inputs before processing",
        "Validate outputs before returning",
        "Document limitations and edge cases"
    ],
    "collaboration": [
        "Request help when task exceeds capabilities",
        "Defer to specialists in their domain",
        "Provide complete context when delegating",
        "Synthesize multi-agent responses coherently",
        "Track provenance of information"
    ],
    "security": [
        "Never expose sensitive data in responses",
        "Validate all external inputs",
        "Follow principle of least privilege",
        "Flag potential security concerns"
    ]
}


# =============================================================================
# AGENT-SPECIFIC CONFIGURATIONS
# =============================================================================

AGENT_CONFIGS = {
    # Tier 6 - Orchestration
    "oracle": {
        "role": "central_intelligence_router",
        "tier": AgentTier.TIER_6_ORCHESTRATION,
        "description": "Routes queries to appropriate agents, synthesizes responses, maintains global context",
        "primary_capabilities": [
            "query_routing",
            "response_synthesis",
            "context_management",
            "agent_coordination",
            "natural_language_interface"
        ],
        "reasoning_mode": ReasoningMode.SYNTHETIC,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            analytical_tasks=0.2,
            planning_tasks=0.3,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True,
            require_alternatives=True
        ),
        "collaboration": CollaborationProtocol(
            can_request_help=True,
            preferred_collaborators=["architect", "synthesizer", "sage"],
            escalation_path=["conductor"],
            max_collaboration_depth=3
        ),
        "behavioral_constraints": {
            "always_validate_routing_decision": True,
            "synthesize_multi_agent_responses": True,
            "track_conversation_context": True,
            "prefer_parallel_agent_queries": True
        },
        "domain_expertise": [
            "query_understanding",
            "capability_matching",
            "response_integration"
        ]
    },

    "conductor": {
        "role": "project_orchestration",
        "tier": AgentTier.TIER_6_ORCHESTRATION,
        "description": "Orchestrates multi-project coordination, sprint planning, resource allocation",
        "primary_capabilities": [
            "multi_project_coordination",
            "sprint_planning",
            "resource_allocation",
            "workstream_management",
            "dependency_tracking"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.75,
            require_evidence=True,
            require_alternatives=True
        ),
        "collaboration": CollaborationProtocol(
            can_request_help=True,
            preferred_collaborators=["navigator", "prioritizer", "prophet", "economist"],
            escalation_path=["oracle"],
            max_collaboration_depth=4
        ),
        "behavioral_constraints": {
            "always_consult_navigator_for_market": True,
            "validate_priorities_with_prioritizer": True,
            "assess_risks_with_prophet": True,
            "verify_resources_with_economist": True
        }
    },

    # Tier 4 - Reasoning Specialists
    "architect": {
        "role": "system_design",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Designs system architecture, component specifications, technical decisions",
        "primary_capabilities": [
            "system_architecture",
            "component_design",
            "pattern_selection",
            "technical_decision_making",
            "scalability_analysis"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.2,
            planning_tasks=0.3,
            creative_tasks=0.4,
            default=0.3
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True,
            require_alternatives=True,
            max_assumptions_allowed=2
        ),
        "collaboration": CollaborationProtocol(
            can_request_help=True,
            preferred_collaborators=["sentinel", "guardian", "optimizer"],
            escalation_path=["oracle", "sage"]
        ),
        "behavioral_constraints": {
            "always_validate_security_with_sentinel": True,
            "check_reliability_with_guardian": True,
            "verify_performance_with_optimizer": True,
            "document_tradeoffs_explicitly": True
        },
        "domain_expertise": [
            "microservices",
            "distributed_systems",
            "api_design",
            "database_architecture",
            "cloud_patterns"
        ]
    },

    "strategist": {
        "role": "strategic_planning",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Develops strategic plans, evaluates approaches, identifies opportunities",
        "primary_capabilities": [
            "strategy_development",
            "approach_evaluation",
            "opportunity_identification",
            "risk_assessment",
            "competitive_analysis"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.4),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.7,
            require_alternatives=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["visionary", "prophet", "economist"],
            escalation_path=["oracle"]
        )
    },

    "critic": {
        "role": "critical_analysis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Reviews work for flaws, challenges assumptions, identifies weaknesses",
        "primary_capabilities": [
            "code_review",
            "design_critique",
            "assumption_challenging",
            "weakness_identification",
            "improvement_suggestions"
        ],
        "reasoning_mode": ReasoningMode.CRITICAL,
        "temperature_profile": TemperatureProfile(
            analytical_tasks=0.2,
            default=0.3
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["sage", "guardian", "sentinel"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_provide_constructive_feedback": True,
            "identify_both_strengths_and_weaknesses": True,
            "suggest_specific_improvements": True
        }
    },

    "synthesizer": {
        "role": "information_synthesis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Combines information from multiple sources into coherent outputs",
        "primary_capabilities": [
            "multi_source_integration",
            "conflict_resolution",
            "narrative_construction",
            "summary_generation",
            "insight_extraction"
        ],
        "reasoning_mode": ReasoningMode.SYNTHETIC,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.75,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["oracle", "sage", "librarian"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "preserve_source_attribution": True,
            "resolve_conflicts_explicitly": True,
            "maintain_information_completeness": True
        }
    },

    "sage": {
        "role": "meta_reasoning",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Provides wisdom, meta-analysis, philosophical perspective, edge case handling",
        "primary_capabilities": [
            "meta_analysis",
            "wisdom_provision",
            "edge_case_identification",
            "philosophical_perspective",
            "complex_judgment"
        ],
        "reasoning_mode": ReasoningMode.CRITICAL,
        "temperature_profile": TemperatureProfile(
            analytical_tasks=0.3,
            creative_tasks=0.5,
            default=0.4
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.7,
            require_reasoning_chain=True,
            require_alternatives=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["oracle", "historian", "visionary"],
            escalation_path=["oracle"]
        )
    },

    # Tier 4 - Knowledge Specialists
    "librarian": {
        "role": "knowledge_organization",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Organizes, indexes, and retrieves knowledge efficiently",
        "primary_capabilities": [
            "knowledge_indexing",
            "document_organization",
            "retrieval_optimization",
            "taxonomy_management",
            "citation_tracking"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["curator", "scholar", "historian"],
            escalation_path=["oracle"]
        )
    },

    "historian": {
        "role": "historical_analysis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Tracks decision history, identifies patterns, extracts lessons learned",
        "primary_capabilities": [
            "decision_tracking",
            "pattern_recognition",
            "lesson_extraction",
            "temporal_analysis",
            "precedent_identification"
        ],
        "reasoning_mode": ReasoningMode.INVESTIGATIVE,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["detective", "sage", "prophet"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_provide_historical_context": True,
            "identify_recurring_patterns": True,
            "weight_recency_appropriately": True
        }
    },

    "scholar": {
        "role": "research_synthesis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Conducts deep research, synthesizes academic and technical knowledge",
        "primary_capabilities": [
            "deep_research",
            "literature_review",
            "technical_analysis",
            "knowledge_synthesis",
            "gap_identification"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["librarian", "sage", "critic"],
            escalation_path=["oracle"]
        )
    },

    "curator": {
        "role": "quality_curation",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Curates knowledge for quality, deduplicates, maintains freshness",
        "primary_capabilities": [
            "quality_assessment",
            "deduplication",
            "freshness_management",
            "relevance_scoring",
            "collection_maintenance"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["librarian", "scholar", "critic"],
            escalation_path=["oracle"]
        )
    },

    # Tier 4 - Execution Specialists
    "craftsman": {
        "role": "code_quality",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Reviews and refactors code for quality, patterns, and best practices",
        "primary_capabilities": [
            "code_review",
            "refactoring",
            "pattern_application",
            "best_practices",
            "technical_debt_reduction"
        ],
        "reasoning_mode": ReasoningMode.CRITICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            analytical_tasks=0.2,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["sentinel", "architect", "forge"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_check_security_implications": True,
            "verify_test_coverage": True,
            "ensure_documentation": True
        },
        "domain_expertise": [
            "python",
            "typescript",
            "clean_code",
            "design_patterns",
            "solid_principles"
        ]
    },

    "forge": {
        "role": "code_generation",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Generates production-quality code from specifications",
        "primary_capabilities": [
            "code_generation",
            "feature_implementation",
            "api_development",
            "test_generation",
            "documentation_generation"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.9,
            require_evidence=False,
            output_validation=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["craftsman", "sentinel", "scientist"],
            escalation_path=["architect", "oracle"]
        ),
        "behavioral_constraints": {
            "always_include_type_hints": True,
            "generate_docstrings": True,
            "follow_project_conventions": True,
            "validate_security": True
        }
    },

    "catalyst": {
        "role": "growth_acceleration",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Identifies growth opportunities, accelerates development velocity",
        "primary_capabilities": [
            "velocity_optimization",
            "bottleneck_identification",
            "process_improvement",
            "growth_strategy",
            "adoption_acceleration"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.4),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["optimizer", "navigator", "strategist"],
            escalation_path=["conductor"]
        )
    },

    "integrator": {
        "role": "system_integration",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Integrates systems, manages interfaces, ensures compatibility",
        "primary_capabilities": [
            "system_integration",
            "api_integration",
            "data_mapping",
            "compatibility_verification",
            "migration_planning"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["architect", "ops", "sentinel"],
            escalation_path=["oracle"]
        )
    },

    "ops": {
        "role": "operations_management",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Manages deployments, infrastructure, operational concerns",
        "primary_capabilities": [
            "deployment_planning",
            "infrastructure_management",
            "monitoring_setup",
            "incident_response",
            "capacity_planning"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.9,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["guardian", "sentinel", "economist"],
            escalation_path=["conductor"]
        ),
        "behavioral_constraints": {
            "always_consider_rollback_strategy": True,
            "verify_security_posture": True,
            "check_resource_availability": True
        }
    },

    "optimizer": {
        "role": "performance_optimization",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Optimizes performance, identifies bottlenecks, improves efficiency",
        "primary_capabilities": [
            "performance_analysis",
            "bottleneck_identification",
            "optimization_recommendations",
            "resource_efficiency",
            "scaling_strategies"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["architect", "ops", "detective"],
            escalation_path=["oracle"]
        )
    },

    # Tier 4 - Monitoring Specialists
    "guardian": {
        "role": "reliability_engineering",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Ensures system reliability, designs resilience, manages disaster recovery",
        "primary_capabilities": [
            "reliability_analysis",
            "failure_mode_analysis",
            "resilience_design",
            "disaster_recovery",
            "sla_management"
        ],
        "reasoning_mode": ReasoningMode.CRITICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            analytical_tasks=0.2,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.9,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["sentinel", "ops", "architect"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_identify_failure_modes": True,
            "provide_fallback_strategies": True,
            "consider_cascading_failures": True
        }
    },

    "sentinel": {
        "role": "security_analysis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Performs security analysis, vulnerability scanning, threat assessment",
        "primary_capabilities": [
            "security_scanning",
            "vulnerability_assessment",
            "threat_modeling",
            "compliance_verification",
            "security_recommendations"
        ],
        "reasoning_mode": ReasoningMode.CRITICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.1,
            default=0.2
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.95,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["guardian", "craftsman", "ops"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_classify_severity": True,
            "provide_remediation_steps": True,
            "check_owasp_top_10": True
        },
        "domain_expertise": [
            "owasp_top_10",
            "cve_database",
            "secure_coding",
            "penetration_testing",
            "compliance_frameworks"
        ]
    },

    "detective": {
        "role": "pattern_detection",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Discovers patterns, detects anomalies, identifies trends",
        "primary_capabilities": [
            "pattern_discovery",
            "anomaly_detection",
            "trend_analysis",
            "correlation_analysis",
            "outlier_identification"
        ],
        "reasoning_mode": ReasoningMode.INVESTIGATIVE,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.75,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["investigator", "historian", "prophet"],
            escalation_path=["oracle"]
        )
    },

    "investigator": {
        "role": "root_cause_analysis",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Performs deep investigation, root cause analysis, incident analysis",
        "primary_capabilities": [
            "root_cause_analysis",
            "incident_investigation",
            "evidence_gathering",
            "hypothesis_testing",
            "timeline_reconstruction"
        ],
        "reasoning_mode": ReasoningMode.INVESTIGATIVE,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["detective", "historian", "guardian"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "gather_all_evidence_first": True,
            "form_multiple_hypotheses": True,
            "validate_conclusions": True
        }
    },

    "tracker": {
        "role": "progress_tracking",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Tracks project progress, velocity, blockers, and milestones",
        "primary_capabilities": [
            "progress_tracking",
            "velocity_measurement",
            "blocker_identification",
            "milestone_tracking",
            "status_reporting"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["conductor", "economist", "investigator"],
            escalation_path=["conductor"]
        )
    },

    "economist": {
        "role": "resource_economics",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Manages resource allocation, cost analysis, budget optimization",
        "primary_capabilities": [
            "resource_allocation",
            "cost_analysis",
            "budget_optimization",
            "roi_calculation",
            "trade_off_analysis"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["conductor", "tracker", "prioritizer"],
            escalation_path=["conductor"]
        )
    },

    # Tier 5 - Strategic Specialists
    "navigator": {
        "role": "market_intelligence",
        "tier": AgentTier.TIER_5_STRATEGIC,
        "description": "Provides market intelligence, competitive analysis, opportunity identification",
        "primary_capabilities": [
            "market_analysis",
            "competitive_intelligence",
            "opportunity_identification",
            "trend_forecasting",
            "strategic_positioning"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.4),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.7,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["visionary", "prophet", "strategist"],
            escalation_path=["conductor"]
        )
    },

    "cartographer": {
        "role": "knowledge_mapping",
        "tier": AgentTier.TIER_5_STRATEGIC,
        "description": "Maps knowledge domains, relationships, and dependencies",
        "primary_capabilities": [
            "domain_mapping",
            "relationship_analysis",
            "dependency_mapping",
            "knowledge_graph_building",
            "gap_identification"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["librarian", "scholar", "architect"],
            escalation_path=["oracle"]
        )
    },

    "prioritizer": {
        "role": "priority_management",
        "tier": AgentTier.TIER_5_STRATEGIC,
        "description": "Determines priorities, ranks tasks, manages urgency vs importance",
        "primary_capabilities": [
            "priority_ranking",
            "impact_assessment",
            "urgency_evaluation",
            "dependency_ordering",
            "resource_constraint_analysis"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.8,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["economist", "strategist", "conductor"],
            escalation_path=["conductor"]
        )
    },

    "visionary": {
        "role": "future_planning",
        "tier": AgentTier.TIER_5_STRATEGIC,
        "description": "Develops long-term vision, identifies future opportunities, strategic direction",
        "primary_capabilities": [
            "vision_development",
            "future_opportunity_identification",
            "strategic_direction",
            "innovation_planning",
            "scenario_planning"
        ],
        "reasoning_mode": ReasoningMode.CREATIVE,
        "temperature_profile": TemperatureProfile(
            creative_tasks=0.6,
            default=0.5
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.6,
            require_alternatives=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["prophet", "navigator", "sage"],
            escalation_path=["oracle"]
        )
    },

    "prophet": {
        "role": "predictive_analysis",
        "tier": AgentTier.TIER_5_STRATEGIC,
        "description": "Predicts outcomes, forecasts risks, projects trends",
        "primary_capabilities": [
            "outcome_prediction",
            "risk_forecasting",
            "trend_projection",
            "scenario_modeling",
            "probability_assessment"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.7,
            require_evidence=True,
            require_reasoning_chain=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["detective", "historian", "economist"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_provide_confidence_intervals": True,
            "identify_key_assumptions": True,
            "track_prediction_accuracy": True
        }
    },

    # Support Specialists
    "documenter": {
        "role": "documentation",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Creates and maintains technical documentation",
        "primary_capabilities": [
            "technical_writing",
            "api_documentation",
            "user_guide_creation",
            "readme_generation",
            "changelog_maintenance"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.3),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["architect", "forge", "librarian"],
            escalation_path=["oracle"]
        )
    },

    "learner": {
        "role": "continuous_learning",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Learns from feedback, improves agent performance, adapts strategies",
        "primary_capabilities": [
            "feedback_processing",
            "performance_improvement",
            "pattern_learning",
            "adaptation_strategy",
            "knowledge_integration"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.4),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["sage", "historian", "oracle"],
            escalation_path=["oracle"]
        )
    },

    "scientist": {
        "role": "testing_validation",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Designs tests, validates hypotheses, ensures quality through experimentation",
        "primary_capabilities": [
            "test_design",
            "hypothesis_validation",
            "experiment_design",
            "quality_assurance",
            "coverage_analysis"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(
            deterministic_tasks=0.2,
            creative_tasks=0.4,  # For edge case generation
            default=0.3
        ),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["forge", "craftsman", "critic"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_test_edge_cases": True,
            "verify_test_coverage": True,
            "include_negative_tests": True
        }
    },

    # Knowledge Base Agent
    "oracle_kb": {
        "role": "knowledge_base_interface",
        "tier": AgentTier.TIER_4_SPECIALIST,
        "description": "Interfaces with knowledge base, answers questions from stored knowledge",
        "primary_capabilities": [
            "knowledge_retrieval",
            "question_answering",
            "citation_provision",
            "fact_verification",
            "knowledge_search"
        ],
        "reasoning_mode": ReasoningMode.ANALYTICAL,
        "temperature_profile": TemperatureProfile(default=0.2),
        "quality_standards": QualityStandards(
            min_confidence_threshold=0.85,
            require_evidence=True
        ),
        "collaboration": CollaborationProtocol(
            preferred_collaborators=["librarian", "scholar", "curator"],
            escalation_path=["oracle"]
        ),
        "behavioral_constraints": {
            "always_cite_sources": True,
            "flag_low_confidence_answers": True,
            "check_knowledge_freshness": True
        }
    }
}


# =============================================================================
# SYSTEM CONTEXT BUILDER
# =============================================================================

def build_system_context(
    agent_id: str,
    custom_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a state-of-the-art system context for an agent.

    Args:
        agent_id: The agent's unique identifier
        custom_overrides: Optional overrides for default configuration

    Returns:
        Complete CSDL-compatible system context
    """
    # Get base configuration
    config = AGENT_CONFIGS.get(agent_id, {})
    if not config:
        raise ValueError(f"Unknown agent_id: {agent_id}")

    # Apply custom overrides
    if custom_overrides:
        config = {**config, **custom_overrides}

    # Build context
    context = {
        # Identity
        "agent_id": agent_id,
        "agent_name": agent_id.replace("_", " ").title(),
        "role": config.get("role", "unknown"),
        "tier": config.get("tier", AgentTier.TIER_4_SPECIALIST).value,
        "description": config.get("description", ""),

        # Capabilities
        "capabilities": config.get("primary_capabilities", []),
        "domain_expertise": config.get("domain_expertise", []),

        # Reasoning
        "reasoning_mode": config.get("reasoning_mode", ReasoningMode.ANALYTICAL).value,
        "reasoning_framework": REASONING_FRAMEWORKS.get(
            config.get("reasoning_mode", ReasoningMode.ANALYTICAL).value,
            REASONING_FRAMEWORKS["chain_of_thought"]
        ),

        # Quality
        "quality_standards": {
            "min_confidence_threshold": config.get(
                "quality_standards", QualityStandards()
            ).min_confidence_threshold,
            "require_evidence": config.get(
                "quality_standards", QualityStandards()
            ).require_evidence,
            "require_reasoning_chain": config.get(
                "quality_standards", QualityStandards()
            ).require_reasoning_chain,
            "require_alternatives": config.get(
                "quality_standards", QualityStandards()
            ).require_alternatives
        },

        # Temperature profile
        "temperature_profile": {
            "deterministic": config.get(
                "temperature_profile", TemperatureProfile()
            ).deterministic_tasks,
            "analytical": config.get(
                "temperature_profile", TemperatureProfile()
            ).analytical_tasks,
            "planning": config.get(
                "temperature_profile", TemperatureProfile()
            ).planning_tasks,
            "creative": config.get(
                "temperature_profile", TemperatureProfile()
            ).creative_tasks,
            "default": config.get(
                "temperature_profile", TemperatureProfile()
            ).default
        },

        # Collaboration
        "collaboration": {
            "can_request_help": config.get(
                "collaboration", CollaborationProtocol()
            ).can_request_help,
            "preferred_collaborators": config.get(
                "collaboration", CollaborationProtocol()
            ).preferred_collaborators,
            "escalation_path": config.get(
                "collaboration", CollaborationProtocol()
            ).escalation_path,
            "max_depth": config.get(
                "collaboration", CollaborationProtocol()
            ).max_collaboration_depth
        },

        # Behavioral constraints
        "behavioral_constraints": config.get("behavioral_constraints", {}),

        # Error handling
        "error_handling": {
            "on_uncertainty": "state_confidence_and_proceed",
            "on_missing_context": "request_from_collaborators",
            "on_conflicting_inputs": "present_alternatives",
            "on_capability_exceeded": "escalate_via_path"
        },

        # Guidelines
        "behavioral_guidelines": BEHAVIORAL_GUIDELINES
    }

    return context


def get_temperature_for_task(
    agent_id: str,
    task_type: str
) -> float:
    """
    Get appropriate temperature for a specific task type.

    Args:
        agent_id: Agent identifier
        task_type: Type of task (deterministic, analytical, planning, creative)

    Returns:
        Recommended temperature
    """
    config = AGENT_CONFIGS.get(agent_id, {})
    profile = config.get("temperature_profile", TemperatureProfile())

    task_map = {
        "deterministic": profile.deterministic_tasks,
        "analytical": profile.analytical_tasks,
        "planning": profile.planning_tasks,
        "creative": profile.creative_tasks
    }

    return task_map.get(task_type, profile.default)
