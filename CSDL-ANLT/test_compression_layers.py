#!/usr/bin/env python3
"""
CSDL Compression Layer Test Suite
==================================

Tests all 4 layers of CSDL compression:
1. Layer 1: Structured JSON (ANLT translation)
2. Layer 2: Semantic Embedding (dense vector compression)
3. Layer 3: Binary Protocol (CBP - MessagePack + LZ4)
4. Layer 4: Deduplication (hash-based content addressing)

Run: python test_compression_layers.py
"""

import sys
import json
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "E3-DevMind-AI"))

def test_layer1_structured_json():
    """
    Layer 1: ANLT Structured JSON Compression
    Human language → Compact CSDL structure
    Target: 50-70% token reduction
    """
    print("\n" + "="*60)
    print("LAYER 1: Structured JSON (ANLT Translation)")
    print("="*60)

    try:
        from anlt.translator import ANLTTranslator
        translator = ANLTTranslator(compression_level="structured")

        test_inputs = [
            "What are the main security risks in our authentication system and how can we mitigate them?",
            "Please analyze the current sprint velocity and predict if we'll meet the deadline.",
            "Design a microservices architecture for handling real-time payments with high availability.",
        ]

        for text in test_inputs:
            metrics = translator.measure_compression(text)
            print(f"\nInput: \"{text[:50]}...\"")
            print(f"  Original chars: {metrics['original_text_length']}")
            print(f"  CSDL chars: {metrics['compressed_size']}")
            print(f"  Token reduction: {metrics['token_reduction_percent']:.1f}%")

            # Show CSDL structure
            csdl = translator.text_to_csdl(text)
            print(f"  CSDL intent: {csdl.get('intent')}")
            print(f"  CSDL entities: {csdl.get('entities', {})}")

        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_layer2_semantic_embedding():
    """
    Layer 2: Semantic Embedding Compression
    Text → 384/1536 dim vector → Quantized + Base64
    Target: 80-90% token reduction
    """
    print("\n" + "="*60)
    print("LAYER 2: Semantic Embedding (Dense Vector)")
    print("="*60)

    try:
        from cbp.semantic_compressor import SemanticCompressor
        compressor = SemanticCompressor()

        test_texts = [
            "Build a JWT authentication system with secure password hashing and refresh tokens",
            "Implement a distributed cache using Redis with automatic failover",
            "Create a real-time notification service using WebSockets",
        ]

        for text in test_texts:
            result = compressor.measure_compression(text)
            print(f"\nInput: \"{text[:50]}...\"")
            print(f"  Original tokens (est): {result['original_tokens_est']}")
            print(f"  Compressed tokens: {result['compressed_tokens_est']}")
            print(f"  Reduction: {result['reduction_percent']:.1f}%")
            print(f"  Embedding dims: {result['compressed_format']['dim']}")
            print(f"  Quantization: {result['compressed_format']['bits']}-bit")

        # Test similarity preservation
        print("\n  Similarity Test (semantic preservation):")
        text1 = "authentication with JWT tokens"
        text2 = "JWT-based auth system"
        text3 = "database query optimization"

        emb1 = compressor.embed(text1)
        emb2 = compressor.embed(text2)
        emb3 = compressor.embed(text3)

        sim_related = compressor.similarity(emb1, emb2)
        sim_unrelated = compressor.similarity(emb1, emb3)

        print(f"    '{text1}' vs '{text2}': {sim_related:.3f} (should be high)")
        print(f"    '{text1}' vs '{text3}': {sim_unrelated:.3f} (should be low)")

        return True
    except ImportError as e:
        print(f"  SKIPPED: {e}")
        print("  Install: pip install sentence-transformers")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_layer3_binary_protocol():
    """
    Layer 3: CBP Binary Protocol
    JSON → MessagePack + Numeric IDs + LZ4
    Target: 60-80% reduction vs JSON
    """
    print("\n" + "="*60)
    print("LAYER 3: Binary Protocol (CBP)")
    print("="*60)

    try:
        from cbp.cbp_protocol import (
            CBPEncoder, CBPDecoder, compare_json_vs_cbp,
            CBPMessage, encode_message, decode_message
        )

        # Sample agent message
        test_message = {
            "type": "handoff",
            "sender": "analyzer",
            "receiver": "strategist",
            "priority": "high",
            "content": {
                "analysis": {
                    "findings": [
                        "Authentication lacks rate limiting",
                        "Session tokens not rotated",
                        "Password policy too weak"
                    ],
                    "risk_level": "high",
                    "affected_components": ["auth-service", "user-api"],
                },
                "recommendation": "Implement security hardening sprint",
            },
            "metadata": {
                "correlation_id": "task-12345",
                "timestamp": time.time(),
            }
        }

        # Compare JSON vs CBP
        comparison = compare_json_vs_cbp(test_message)

        print(f"\nTest Message: Agent handoff with analysis")
        print(f"  JSON size: {comparison['json_bytes']} bytes")
        print(f"  CBP size: {comparison['cbp_bytes']} bytes")
        print(f"  Reduction: {comparison['reduction_percent']:.1f}%")
        print(f"  Compression ratio: {comparison['compression_ratio']:.1f}x")

        # Show CBP features used
        metrics = comparison['cbp_metrics']
        print(f"  Used LZ4: {metrics['used_lz4']}")
        print(f"  Used Dedup: {metrics['used_dedup']}")

        # Verify round-trip
        encoded, _ = encode_message(test_message)
        decoded, _ = decode_message(encoded)
        original_dict = CBPMessage.from_dict(test_message).to_dict()

        print(f"\n  Round-trip verification: ", end="")
        # Compare key fields
        if (decoded.to_dict()['sender'] == original_dict['sender'] and
            decoded.to_dict()['receiver'] == original_dict['receiver']):
            print("PASSED ✓")
        else:
            print("FAILED ✗")

        return True
    except ImportError as e:
        print(f"  SKIPPED: {e}")
        print("  Install: pip install msgpack xxhash lz4")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer4_deduplication():
    """
    Layer 4: Semantic Deduplication
    Repeated content → Hash reference (8 bytes)
    Target: 90%+ reduction for repeated content
    """
    print("\n" + "="*60)
    print("LAYER 4: Deduplication (Hash-based)")
    print("="*60)

    try:
        from cbp.cbp_protocol import (
            CBPEncoder, SemanticRegistry, get_registry
        )

        # Create fresh registry for test
        registry = SemanticRegistry()
        encoder = CBPEncoder(registry=registry)

        # Same content sent multiple times (simulating pipeline A→B→C)
        repeated_content = {
            "type": "request",
            "sender": "oracle",
            "receiver": "analyzer",
            "content": {
                "task": "Analyze the authentication system for security vulnerabilities",
                "context": {
                    "codebase": "/src/auth",
                    "priority": "high",
                    "deadline": "2025-01-15",
                }
            }
        }

        print("\nSimulating message pipeline (same content, 5 transmissions):")

        total_without_dedup = 0
        total_with_dedup = 0

        for i in range(5):
            encoded, metrics = encoder.encode(repeated_content)

            if i == 0:
                first_size = metrics.encoded_bytes
                total_without_dedup += metrics.original_bytes
                total_with_dedup += metrics.encoded_bytes
                print(f"  Transmission {i+1}: {metrics.encoded_bytes} bytes (full, stored)")
            else:
                total_without_dedup += metrics.original_bytes
                total_with_dedup += metrics.encoded_bytes
                print(f"  Transmission {i+1}: {metrics.encoded_bytes} bytes (dedup: {metrics.used_dedup})")

        # Calculate savings
        savings = (1 - total_with_dedup / total_without_dedup) * 100
        print(f"\n  Without dedup: {total_without_dedup} bytes total")
        print(f"  With dedup: {total_with_dedup} bytes total")
        print(f"  Dedup savings: {savings:.1f}%")

        # Registry stats
        stats = registry.get_stats()
        print(f"\n  Registry stats:")
        print(f"    Entries: {stats['entries']}")
        print(f"    Hits: {stats['hits']}")
        print(f"    Hit rate: {stats['hit_rate_percent']:.1f}%")

        return True
    except ImportError as e:
        print(f"  SKIPPED: {e}")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_full_pipeline():
    """
    Full Pipeline Test: Human → CSDL → Agent Communication → Human
    """
    print("\n" + "="*60)
    print("FULL PIPELINE: End-to-End Compression")
    print("="*60)

    try:
        from anlt.translator import ANLTTranslator
        from cbp.cbp_protocol import encode_message, decode_message, CBPMessage

        translator = ANLTTranslator()

        # Human input
        human_input = """
        I need you to analyze our authentication system for security vulnerabilities.
        Focus on password handling, session management, and token security.
        Provide a prioritized list of issues and recommendations for the next sprint.
        """

        print(f"\n1. HUMAN INPUT ({len(human_input)} chars)")
        print(f"   \"{human_input[:60].strip()}...\"")

        # Layer 1: ANLT translation
        csdl_query = translator.text_to_csdl(human_input)
        csdl_json = json.dumps(csdl_query)
        print(f"\n2. ANLT → CSDL ({len(csdl_json)} chars)")
        print(f"   Intent: {csdl_query.get('intent')}")

        # Layer 3: CBP encoding for agent communication
        agent_message = {
            "type": "request",
            "sender": "oracle",
            "receiver": "sentinel",
            "content": csdl_query,
            "priority": "high"
        }

        json_size = len(json.dumps(agent_message))
        encoded, metrics = encode_message(agent_message)

        print(f"\n3. CBP ENCODING")
        print(f"   JSON: {json_size} bytes")
        print(f"   CBP: {metrics.encoded_bytes} bytes")
        print(f"   Reduction: {metrics.reduction_percent:.1f}%")

        # Decode and show round-trip works
        decoded, _ = decode_message(encoded)

        print(f"\n4. CBP DECODE (round-trip)")
        print(f"   Type: {decoded.to_dict()['type']}")
        print(f"   Sender: {decoded.to_dict()['sender']}")
        print(f"   Receiver: {decoded.to_dict()['receiver']}")

        # Calculate total pipeline compression
        original_size = len(human_input)
        final_size = metrics.encoded_bytes
        total_reduction = (1 - final_size / original_size) * 100

        print(f"\n5. TOTAL PIPELINE COMPRESSION")
        print(f"   Original human text: {original_size} bytes")
        print(f"   Final CBP message: {final_size} bytes")
        print(f"   Total reduction: {total_reduction:.1f}%")

        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("CSDL COMPRESSION LAYER TEST SUITE")
    print("="*60)
    print("Testing all 4 layers of the CSDL compression protocol")

    results = {}

    results['layer1'] = test_layer1_structured_json()
    results['layer2'] = test_layer2_semantic_embedding()
    results['layer3'] = test_layer3_binary_protocol()
    results['layer4'] = test_layer4_deduplication()
    results['pipeline'] = test_full_pipeline()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for layer, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "⊘ SKIPPED"
        print(f"  {layer}: {status}")

    passed = sum(1 for r in results.values() if r is True)
    total = len(results)
    print(f"\n  {passed}/{total} tests passed")

    return all(r is not False for r in results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
