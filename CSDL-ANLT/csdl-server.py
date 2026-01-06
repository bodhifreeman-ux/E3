#!/usr/bin/env python3
"""
CSDL-14B Inference Server
Uses HuggingFace Transformers with proper tokenization (bypasses llama.cpp bug)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CSDL-14B Server")

# Global model and tokenizer
model = None
tokenizer = None

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

def load_model():
    """Load CSDL-14B model with proper tokenization"""
    global model, tokenizer

    model_path = "/home/bodhifreeman/E3/csdl-14b/model/merged_16bit"

    logger.info(f"Loading model from {model_path}...")

    # Load tokenizer with proper settings
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        use_fast=True
    )

    # Load model on CPU (temporary - need CUDA-enabled PyTorch)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float32,
        device_map="cpu",
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )

    model.eval()
    logger.info("Model loaded successfully!")

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

# Ollama-compatible endpoints for model discovery
@app.get("/api/tags")
async def ollama_tags():
    """Ollama-compatible model list endpoint for integration with Archon/OpenWebUI"""
    import time
    return {
        "models": [
            {
                "name": "csdl-14b:latest",
                "model": "csdl-14b:latest",
                "modified_at": "2025-01-06T00:00:00Z",
                "size": 28000000000,  # ~28GB
                "digest": "sha256:csdl14b",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "qwen2.5",
                    "families": ["qwen2.5"],
                    "parameter_size": "14B",
                    "quantization_level": "f16"
                }
            }
        ]
    }

@app.get("/api/version")
async def ollama_version():
    """Ollama-compatible version endpoint"""
    return {"version": "0.1.0"}

@app.post("/api/chat")
async def ollama_chat(request: dict):
    """Ollama-compatible chat endpoint"""
    import time

    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        messages = request.get("messages", [])

        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = tokenizer(text, return_tensors="pt").to("cuda:0")

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.get("options", {}).get("num_predict", 512),
                temperature=request.get("options", {}).get("temperature", 0.7),
                top_p=request.get("options", {}).get("top_p", 0.9),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode
        generated_text = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        return {
            "model": request.get("model", "csdl-14b"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message": {
                "role": "assistant",
                "content": generated_text
            },
            "done": True,
            "total_duration": 0,
            "prompt_eval_count": inputs['input_ids'].shape[1],
            "eval_count": outputs.shape[1] - inputs['input_ids'].shape[1]
        }

    except Exception as e:
        logger.error(f"Ollama chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Format messages using Qwen2.5 chat template
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = tokenizer(text, return_tensors="pt").to("cuda:0")

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode
        generated_text = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        # Build response
        import time
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": inputs['input_ids'].shape[1],
                "completion_tokens": outputs.shape[1] - inputs['input_ids'].shape[1],
                "total_tokens": outputs.shape[1]
            }
        }

        return response

    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("CSDL_SERVER_PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
