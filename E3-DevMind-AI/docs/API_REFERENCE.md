# E3 DevMind AI - API Reference

Complete API documentation for E3 DevMind AI.

## Base URL
```
http://localhost:8000
```

## Authentication

Currently no authentication required (will be added for production).

## Endpoints

### Query Endpoints

#### POST /api/query

Process a natural language query through the 32-agent swarm.

**Request Body:**
```json
{
  "query": "What are the risks in our current sprint?",
  "context": {
    "project": "E3-Platform",
    "sprint": 42
  },
  "use_compression": true
}
```

**Response:**
```json
{
  "response": "Analysis of current sprint risks...",
  "metadata": {
    "confidence": 0.95,
    "query_type": "risk_analysis"
  },
  "agents_involved": ["oracle", "prophet", "strategist"],
  "processing_time_ms": 1250.5,
  "tokens_saved": 450
}
```

### Health Endpoints

#### GET /api/health

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-18T10:30:00Z",
  "components": {
    "api": "healthy",
    "csdl_vllm": "healthy",
    "qdrant": "healthy",
    "postgres": "healthy",
    "redis": "healthy"
  }
}
```

### System Endpoints

#### GET /api/status

Get complete system status.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "agents": [...],
  "knowledge_base": {
    "total_documents": 10542,
    "total_vectors": 156234
  },
  "uptime_seconds": 86400.0
}
```

### Knowledge Base Endpoints

#### POST /api/ingest

Ingest documents from directory.

**Request:**
```json
{
  "directory": "/path/to/documents",
  "recursive": true,
  "file_types": ["pdf", "docx"]
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Document ingestion started for /path/to/documents"
}
```

#### GET /api/ingest/{job_id}

Get ingestion job status.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "processed": 45,
  "total": 100,
  "progress_percentage": 45.0
}
```

#### POST /api/knowledge/search

Search knowledge base.

**Request:**
```json
{
  "query": "E3 architecture decisions",
  "limit": 5,
  "filters": {
    "category": "technical"
  }
}
```

**Response:**
```json
{
  "query": "E3 architecture decisions",
  "results": [
    {
      "id": "doc_123",
      "title": "E3 Architecture Overview",
      "excerpt": "Relevant excerpt...",
      "score": 0.95,
      "category": "technical"
    }
  ],
  "total_results": 1
}
```

#### GET /api/knowledge/stats

Get knowledge base statistics.

**Response:**
```json
{
  "total_documents": 10542,
  "total_vectors": 156234,
  "total_size_bytes": 5242880000,
  "categories": {
    "technical": 4521,
    "business": 2134,
    "meeting_notes": 1567,
    "code": 2320
  },
  "last_updated": "2025-11-18T10:30:00Z"
}
```

### Agent Endpoints

#### GET /api/agents

List all available agents.

**Response:**
```json
{
  "total_agents": 32,
  "active_agents": 32,
  "agents": [
    {
      "id": "oracle",
      "name": "Oracle",
      "tier": "coordination",
      "number": 1
    }
  ]
}
```

#### POST /api/agent/{agent_id}/query

Query specific agent directly (for testing/debugging).

**Request:**
```json
{
  "query": "Analyze this code",
  "context": {"file": "app.py"}
}
```

**Response:**
```json
{
  "agent_id": "craftsman",
  "response": "Code analysis...",
  "processing_time_ms": 523.4
}
```

## WebSocket API

### Endpoint: /ws

Real-time communication endpoint.

**Message Format:**
```json
{
  "type": "query" | "subscribe" | "unsubscribe" | "ping",
  "data": {...}
}
```

**Example - Query:**
```json
{
  "type": "query",
  "data": {
    "query": "What are the risks?"
  }
}
```

**Progress Updates:**
```json
{
  "type": "query_progress",
  "step": "coordinating_agents",
  "progress": 0.50,
  "agents_involved": ["oracle", "prophet"]
}
```

**Example - Subscribe to Topic:**
```json
{
  "type": "subscribe",
  "data": {
    "topic": "alerts"
  }
}
```

## Error Responses

All errors follow this format:
```json
{
  "error": "Error description",
  "status_code": 500
}
```

Common status codes:
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
