"""
CSDL Binary Protocol (CBP) - World's first binary protocol for LLM agents.
Achieves 85-98% compression through MessagePack, deduplication, and delta encoding.
"""

from .cbp_schema import (
    AgentID, MessageType, FieldID, TaskID, Priority,
    AGENT_NAME_TO_ID, AGENT_ID_TO_NAME,
    MESSAGE_TYPE_TO_ID, MESSAGE_ID_TO_TYPE,
    FIELD_NAME_TO_ID, FIELD_ID_TO_NAME,
    CBP_MAGIC, CBP_VERSION,
    FLAG_IS_DELTA, FLAG_HAS_HASH, FLAG_COMPRESSED, FLAG_ENCRYPTED,
)

from .cbp_protocol import (
    SemanticRegistry,
    CBPMetrics,
    CBPMessage,
    CBPEncoder,
    CBPDecoder,
    DeltaEncoder,
    encode_message,
    decode_message,
    get_encoder,
    get_decoder,
    get_registry,
    get_delta_encoder,
    compare_json_vs_cbp,
)

from .semantic_compressor import SemanticCompressor

__all__ = [
    # Schema
    'AgentID', 'MessageType', 'FieldID', 'TaskID', 'Priority',
    'AGENT_NAME_TO_ID', 'AGENT_ID_TO_NAME',
    'MESSAGE_TYPE_TO_ID', 'MESSAGE_ID_TO_TYPE',
    'FIELD_NAME_TO_ID', 'FIELD_ID_TO_NAME',
    'CBP_MAGIC', 'CBP_VERSION',
    'FLAG_IS_DELTA', 'FLAG_HAS_HASH', 'FLAG_COMPRESSED', 'FLAG_ENCRYPTED',
    # Protocol
    'SemanticRegistry', 'CBPMetrics', 'CBPMessage',
    'CBPEncoder', 'CBPDecoder', 'DeltaEncoder',
    'encode_message', 'decode_message',
    'get_encoder', 'get_decoder', 'get_registry', 'get_delta_encoder',
    'compare_json_vs_cbp',
    # Semantic
    'SemanticCompressor',
]
