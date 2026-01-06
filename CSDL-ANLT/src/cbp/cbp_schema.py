"""
CSDL Binary Protocol (CBP) - Schema Definitions
================================================
Fixed numeric IDs for all protocol elements.
This enables 90%+ compression vs JSON string keys.

Copyright 2025 LUBTFY. World's first binary agent protocol.
"""

from enum import IntEnum
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════
# Agent IDs (1 byte each)
# ═══════════════════════════════════════════════════════════════════════

class AgentID(IntEnum):
    """Numeric IDs for all agents - 1 byte instead of string names"""
    UNKNOWN = 0x00
    ANALYZER = 0x01
    STRATEGIST = 0x02
    CRITIC = 0x03
    SYNTHESIZER = 0x04
    REFLECTOR = 0x05
    # LUBTFY agents
    LUBTFY_ORCHESTRATOR = 0x10
    LUBTFY_RESEARCHER = 0x11
    LUBTFY_WRITER = 0x12
    LUBTFY_REVIEWER = 0x13
    # Nexus agents
    NEXUS = 0x20
    # System
    USER = 0xFE
    SYSTEM = 0xFF


# String to ID mapping
AGENT_NAME_TO_ID: Dict[str, int] = {
    "analyzer": AgentID.ANALYZER,
    "strategist": AgentID.STRATEGIST,
    "critic": AgentID.CRITIC,
    "synthesizer": AgentID.SYNTHESIZER,
    "reflector": AgentID.REFLECTOR,
    "lubtfy": AgentID.LUBTFY_ORCHESTRATOR,
    "lubtfy_orchestrator": AgentID.LUBTFY_ORCHESTRATOR,
    "researcher": AgentID.LUBTFY_RESEARCHER,
    "writer": AgentID.LUBTFY_WRITER,
    "reviewer": AgentID.LUBTFY_REVIEWER,
    "nexus": AgentID.NEXUS,
    "user": AgentID.USER,
    "system": AgentID.SYSTEM,
}

AGENT_ID_TO_NAME: Dict[int, str] = {v: k for k, v in AGENT_NAME_TO_ID.items()}


# ═══════════════════════════════════════════════════════════════════════
# Message Types (1 byte)
# ═══════════════════════════════════════════════════════════════════════

class MessageType(IntEnum):
    """Message type IDs"""
    REQUEST = 0x01
    RESPONSE = 0x02
    CONTEXT = 0x03
    HANDOFF = 0x04
    FEEDBACK = 0x05
    SYNC = 0x06
    DELTA = 0x07      # Delta-encoded message
    # Federation
    DISCOVER = 0x10
    REGISTER = 0x11
    HEARTBEAT = 0x12


MESSAGE_TYPE_TO_ID: Dict[str, int] = {
    "req": MessageType.REQUEST,
    "res": MessageType.RESPONSE,
    "ctx": MessageType.CONTEXT,
    "hnd": MessageType.HANDOFF,
    "fbk": MessageType.FEEDBACK,
    "syn": MessageType.SYNC,
    "delta": MessageType.DELTA,
    "dsc": MessageType.DISCOVER,
    "reg": MessageType.REGISTER,
    "hbt": MessageType.HEARTBEAT,
}

MESSAGE_ID_TO_TYPE: Dict[int, str] = {v: k for k, v in MESSAGE_TYPE_TO_ID.items()}


# ═══════════════════════════════════════════════════════════════════════
# Field IDs (1 byte each) - Replace JSON string keys
# ═══════════════════════════════════════════════════════════════════════

class FieldID(IntEnum):
    """Field IDs for message structure - 1 byte vs multi-byte strings"""
    # Core message fields
    TYPE = 0x01
    SENDER = 0x02
    RECEIVER = 0x03
    CONTENT = 0x04
    METADATA = 0x05
    TIMESTAMP = 0x06
    MESSAGE_ID = 0x07
    PRIORITY = 0x08

    # Delta/dedup fields
    HASH = 0x10
    DELTA_REF = 0x11
    DELTA_PAYLOAD = 0x12

    # Content fields
    TASK = 0x20
    TARGET = 0x21
    RESULT = 0x22
    CONFIDENCE = 0x23
    REASONING = 0x24
    RECOMMENDATIONS = 0x25
    RISKS = 0x26
    OPPORTUNITIES = 0x27

    # Agent-specific
    ANALYSIS = 0x30
    STRATEGIES = 0x31
    CRITIQUE = 0x32
    SYNTHESIS = 0x33
    REFLECTION = 0x34

    # Nested structures
    KEY_FACTORS = 0x40
    NEXT_STEPS = 0x41
    SUCCESS_METRICS = 0x42
    RISK_MITIGATION = 0x43
    QUALITY_EVAL = 0x44


# Bidirectional mapping
FIELD_NAME_TO_ID: Dict[str, int] = {
    "type": FieldID.TYPE,
    "t": FieldID.TYPE,
    "sender": FieldID.SENDER,
    "s": FieldID.SENDER,
    "receiver": FieldID.RECEIVER,
    "r": FieldID.RECEIVER,
    "content": FieldID.CONTENT,
    "c": FieldID.CONTENT,
    "metadata": FieldID.METADATA,
    "m": FieldID.METADATA,
    "timestamp": FieldID.TIMESTAMP,
    "ts": FieldID.TIMESTAMP,
    "message_id": FieldID.MESSAGE_ID,
    "id": FieldID.MESSAGE_ID,
    "priority": FieldID.PRIORITY,
    "p": FieldID.PRIORITY,
    "hash": FieldID.HASH,
    "delta_ref": FieldID.DELTA_REF,
    "delta_payload": FieldID.DELTA_PAYLOAD,
    "task": FieldID.TASK,
    "tk": FieldID.TASK,
    "target": FieldID.TARGET,
    "result": FieldID.RESULT,
    "rs": FieldID.RESULT,
    "confidence": FieldID.CONFIDENCE,
    "cf": FieldID.CONFIDENCE,
    "reasoning": FieldID.REASONING,
    "rn": FieldID.REASONING,
    "recommendations": FieldID.RECOMMENDATIONS,
    "rc": FieldID.RECOMMENDATIONS,
    "risks": FieldID.RISKS,
    "rk": FieldID.RISKS,
    "opportunities": FieldID.OPPORTUNITIES,
    "op": FieldID.OPPORTUNITIES,
    "analysis": FieldID.ANALYSIS,
    "an": FieldID.ANALYSIS,
    "strategies": FieldID.STRATEGIES,
    "st": FieldID.STRATEGIES,
    "critique": FieldID.CRITIQUE,
    "cr": FieldID.CRITIQUE,
    "synthesis": FieldID.SYNTHESIS,
    "sy": FieldID.SYNTHESIS,
    "reflection": FieldID.REFLECTION,
    "rf": FieldID.REFLECTION,
    "key_factors": FieldID.KEY_FACTORS,
    "kf": FieldID.KEY_FACTORS,
    "next_steps": FieldID.NEXT_STEPS,
    "ns": FieldID.NEXT_STEPS,
    "success_metrics": FieldID.SUCCESS_METRICS,
    "sm": FieldID.SUCCESS_METRICS,
    "risk_mitigation": FieldID.RISK_MITIGATION,
    "rm": FieldID.RISK_MITIGATION,
    "quality_eval": FieldID.QUALITY_EVAL,
    "qe": FieldID.QUALITY_EVAL,
}

FIELD_ID_TO_NAME: Dict[int, str] = {
    FieldID.TYPE: "type",
    FieldID.SENDER: "sender",
    FieldID.RECEIVER: "receiver",
    FieldID.CONTENT: "content",
    FieldID.METADATA: "metadata",
    FieldID.TIMESTAMP: "timestamp",
    FieldID.MESSAGE_ID: "message_id",
    FieldID.PRIORITY: "priority",
    FieldID.HASH: "hash",
    FieldID.DELTA_REF: "delta_ref",
    FieldID.DELTA_PAYLOAD: "delta_payload",
    FieldID.TASK: "task",
    FieldID.TARGET: "target",
    FieldID.RESULT: "result",
    FieldID.CONFIDENCE: "confidence",
    FieldID.REASONING: "reasoning",
    FieldID.RECOMMENDATIONS: "recommendations",
    FieldID.RISKS: "risks",
    FieldID.OPPORTUNITIES: "opportunities",
    FieldID.ANALYSIS: "analysis",
    FieldID.STRATEGIES: "strategies",
    FieldID.CRITIQUE: "critique",
    FieldID.SYNTHESIS: "synthesis",
    FieldID.REFLECTION: "reflection",
    FieldID.KEY_FACTORS: "key_factors",
    FieldID.NEXT_STEPS: "next_steps",
    FieldID.SUCCESS_METRICS: "success_metrics",
    FieldID.RISK_MITIGATION: "risk_mitigation",
    FieldID.QUALITY_EVAL: "quality_eval",
}


# ═══════════════════════════════════════════════════════════════════════
# Task IDs (1 byte) - Common agent tasks
# ═══════════════════════════════════════════════════════════════════════

class TaskID(IntEnum):
    """Common task identifiers"""
    ANALYZE = 0x01
    STRATEGIZE = 0x02
    CRITIQUE = 0x03
    SYNTHESIZE = 0x04
    REFLECT = 0x05
    RESEARCH = 0x06
    WRITE = 0x07
    REVIEW = 0x08
    EXECUTE = 0x09
    VALIDATE = 0x0A


TASK_NAME_TO_ID: Dict[str, int] = {
    "analyze": TaskID.ANALYZE,
    "strategize": TaskID.STRATEGIZE,
    "critique": TaskID.CRITIQUE,
    "synthesize": TaskID.SYNTHESIZE,
    "reflect": TaskID.REFLECT,
    "research": TaskID.RESEARCH,
    "write": TaskID.WRITE,
    "review": TaskID.REVIEW,
    "execute": TaskID.EXECUTE,
    "validate": TaskID.VALIDATE,
}

TASK_ID_TO_NAME: Dict[int, str] = {v: k for k, v in TASK_NAME_TO_ID.items()}


# ═══════════════════════════════════════════════════════════════════════
# Priority Levels (1 byte)
# ═══════════════════════════════════════════════════════════════════════

class Priority(IntEnum):
    LOW = 0x01
    NORMAL = 0x02
    HIGH = 0x03
    CRITICAL = 0x04


PRIORITY_NAME_TO_ID: Dict[str, int] = {
    "low": Priority.LOW,
    "normal": Priority.NORMAL,
    "medium": Priority.NORMAL,
    "high": Priority.HIGH,
    "critical": Priority.CRITICAL,
    "urgent": Priority.CRITICAL,
}

PRIORITY_ID_TO_NAME: Dict[int, str] = {
    Priority.LOW: "low",
    Priority.NORMAL: "normal",
    Priority.HIGH: "high",
    Priority.CRITICAL: "critical",
}


# ═══════════════════════════════════════════════════════════════════════
# CBP Frame Constants
# ═══════════════════════════════════════════════════════════════════════

CBP_MAGIC = b'\xCB\x50'  # "CP" for CSDL Protocol
CBP_VERSION = 0x01

# Flags
FLAG_IS_DELTA = 0x01      # Bit 0: Delta message
FLAG_HAS_HASH = 0x02      # Bit 1: Includes dedup hash
FLAG_COMPRESSED = 0x04    # Bit 2: LZ4 compressed payload
FLAG_ENCRYPTED = 0x08     # Bit 3: Encrypted (future)
