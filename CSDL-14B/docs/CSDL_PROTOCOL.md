# CSDL Protocol Specification

**Version 1.0**

CSDL (Compressed Semantic Data Language) is a structured JSON-based protocol designed for efficient AI agent communication. It provides a standardized format for defining functions, classes, workflows, and inter-agent messages.

## Table of Contents

1. [Design Principles](#design-principles)
2. [Core Types](#core-types)
3. [Type Codes](#type-codes)
4. [Function Definitions](#function-definitions)
5. [Class Definitions](#class-definitions)
6. [Workflow Definitions](#workflow-definitions)
7. [Agent Messages](#agent-messages)
8. [Memory Operations](#memory-operations)
9. [Examples](#examples)

## Design Principles

CSDL is designed with the following principles:

1. **Compression**: Short field names to reduce token usage
2. **Clarity**: Unambiguous structure for machine parsing
3. **Flexibility**: Extensible for various agent architectures
4. **Compatibility**: JSON-based for universal support

## Core Types

### Basic Types

| Type | Description |
|------|-------------|
| `string` | Text data |
| `integer` | Whole numbers |
| `float` | Decimal numbers |
| `boolean` | True/false values |
| `array` | Ordered list of items |
| `object` | Key-value mapping |
| `null` | Null/none value |
| `any` | Any type allowed |

### Complex Types

| Type | Description |
|------|-------------|
| `function` | Callable function definition |
| `class` | Class/object definition |
| `workflow` | Multi-step process |
| `message` | Inter-agent message |
| `memory` | Memory operation |
| `tool` | External tool definition |

## Type Codes

CSDL uses short codes for common fields to minimize token usage:

| Code | Full Name | Description |
|------|-----------|-------------|
| `t` | type | The type of the element |
| `n` | name | Name/identifier |
| `d` | description | Human-readable description |
| `p` | parameters | Input parameters |
| `r` | return/required | Return type or required flag |
| `a` | arguments | Actual argument values |
| `v` | value | Value/content |
| `cx` | confidence | Confidence score (0-1) |
| `m` | metadata | Additional metadata |
| `s` | steps | Workflow steps |
| `c` | children | Child elements |

## Function Definitions

Functions are the core building block of CSDL. They define callable operations with typed parameters and return values.

### Structure

```json
{
  "t": "function",
  "n": "function_name",
  "d": "Description of what the function does",
  "p": {
    "param1": {
      "t": "string",
      "d": "Parameter description",
      "r": true
    },
    "param2": {
      "t": "integer",
      "d": "Optional parameter",
      "r": false,
      "default": 10
    }
  },
  "r": {
    "t": "object",
    "p": ["field1", "field2"]
  }
}
```

### Parameter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `t` | string | Yes | Parameter type |
| `d` | string | No | Description |
| `r` | boolean | No | Required flag (default: false) |
| `default` | any | No | Default value |
| `enum` | array | No | Allowed values |

## Class Definitions

Classes define object structures with properties and methods.

### Structure

```json
{
  "t": "class",
  "n": "ClassName",
  "d": "Class description",
  "p": {
    "property1": {
      "t": "string",
      "d": "Property description"
    }
  },
  "methods": [
    {
      "t": "function",
      "n": "method_name",
      "d": "Method description",
      "p": {},
      "r": {"t": "void"}
    }
  ]
}
```

## Workflow Definitions

Workflows define multi-step processes with conditional branching and loops.

### Structure

```json
{
  "t": "workflow",
  "n": "workflow_name",
  "d": "Workflow description",
  "s": [
    {
      "id": "step1",
      "action": "function_name",
      "a": {"param1": "value"},
      "next": "step2"
    },
    {
      "id": "step2",
      "action": "conditional",
      "condition": "result.success",
      "true_next": "step3",
      "false_next": "error_handler"
    }
  ]
}
```

### Step Types

| Type | Description |
|------|-------------|
| `action` | Execute a function |
| `conditional` | Branch based on condition |
| `loop` | Repeat steps |
| `parallel` | Execute steps concurrently |
| `wait` | Wait for event/condition |

## Agent Messages

Messages define communication between agents.

### Structure

```json
{
  "t": "message",
  "from": "agent_id",
  "to": "target_agent_id",
  "intent": "request|response|notify",
  "v": {
    "action": "requested_action",
    "data": {}
  },
  "cx": 0.95
}
```

### Intent Types

| Intent | Description |
|--------|-------------|
| `request` | Request action from another agent |
| `response` | Response to a request |
| `notify` | Notification (no response expected) |
| `query` | Query for information |
| `error` | Error notification |

## Memory Operations

Memory operations define how agents store and retrieve information.

### Store Operation

```json
{
  "t": "memory",
  "op": "store",
  "key": "memory_key",
  "v": {
    "data": "to store"
  },
  "ttl": 3600,
  "m": {
    "category": "episodic",
    "importance": 0.8
  }
}
```

### Retrieve Operation

```json
{
  "t": "memory",
  "op": "retrieve",
  "query": "search query",
  "filters": {
    "category": "semantic",
    "min_importance": 0.5
  },
  "limit": 10
}
```

### Memory Categories

| Category | Description |
|----------|-------------|
| `working` | Short-term task context |
| `episodic` | Event/experience memories |
| `semantic` | Factual knowledge |
| `procedural` | How-to knowledge |

## Examples

### Complete Function Example

```json
{
  "t": "function",
  "n": "search_knowledge_base",
  "d": "Search the knowledge base for relevant documents using semantic similarity",
  "p": {
    "query": {
      "t": "string",
      "d": "The search query",
      "r": true
    },
    "filters": {
      "t": "object",
      "d": "Optional filters to apply",
      "r": false,
      "p": {
        "category": {"t": "string"},
        "date_from": {"t": "string"},
        "date_to": {"t": "string"}
      }
    },
    "limit": {
      "t": "integer",
      "d": "Maximum number of results",
      "r": false,
      "default": 10
    }
  },
  "r": {
    "t": "array",
    "items": {
      "t": "object",
      "p": {
        "id": {"t": "string"},
        "content": {"t": "string"},
        "score": {"t": "float"},
        "metadata": {"t": "object"}
      }
    }
  },
  "cx": 0.92
}
```

### Agent Coordination Example

```json
{
  "t": "workflow",
  "n": "research_and_report",
  "d": "Coordinate multiple agents to research a topic and generate a report",
  "s": [
    {
      "id": "gather",
      "agent": "atlas",
      "action": "plan_research",
      "a": {"topic": "{{input.topic}}"},
      "next": "search"
    },
    {
      "id": "search",
      "agent": "nexus",
      "action": "execute_searches",
      "a": {"queries": "{{gather.queries}}"},
      "next": "synthesize"
    },
    {
      "id": "synthesize",
      "agent": "marketing",
      "action": "generate_report",
      "a": {
        "findings": "{{search.results}}",
        "format": "markdown"
      },
      "next": "complete"
    }
  ]
}
```

## Validation

CSDL responses should be validated for:

1. **Required fields**: All required fields present
2. **Type correctness**: Values match declared types
3. **Confidence threshold**: `cx` above minimum threshold
4. **Schema compliance**: Structure matches expected format

## Extensions

CSDL can be extended with custom types by:

1. Defining new type codes in the `m` (metadata) field
2. Registering custom validators
3. Documenting extension schema

---

*CSDL Protocol Specification v1.0 - LUBTFY*
