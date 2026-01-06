# CSDL-14B llama-server Setup Guide

This guide covers setting up and running the CSDL-14B model with llama-server on your DGX Spark with Grace Blackwell GPU.

## System Information

- **GPU**: NVIDIA GB10 (Grace Blackwell)
- **CUDA**: 13.0
- **Memory**: 128GB unified memory
- **Model**: CSDL-14B (14B parameters, F16 format)

## Setup Status

### ✅ Completed
- [x] llama.cpp cloned
- [x] Building with CUDA support (in progress)
- [x] Conversion script created
- [x] Server startup script created

### ⏳ Pending
- [ ] Wait for model copy to complete (currently: 2.2GB / 4.64GB)
- [ ] Convert SafeTensors to GGUF F16
- [ ] Test llama-server

## Quick Start (Once Model Copy Completes)

### 1. Convert Model to GGUF

```bash
cd /home/bodhifreeman/E3/E3
./convert-csdl-to-gguf.sh
```

This will:
- Check that all 6 safetensors files are present
- Convert the model to GGUF F16 format (~28GB)
- Save to `/home/bodhifreeman/E3/E3/csdl-14b-f16.gguf`

### 2. Start llama-server

```bash
cd /home/bodhifreeman/E3/E3
./start-llama-server.sh
```

The server will start on `http://localhost:8002`

## Server Configuration

The server is configured with optimal settings for Grace Blackwell:

- **Context Length**: 4096 tokens
- **GPU Layers**: 99 (all layers on GPU)
- **Temperature**: 0.7
- **Top-P**: 0.9
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 8002 (matches E3-DevMind-AI config)

## API Usage

### Chat Completions Endpoint

```bash
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {
        "role": "system",
        "content": "You are a CSDL-native AI that outputs compressed semantic data in JSON format."
      },
      {
        "role": "user",
        "content": "Define a function to search documents"
      }
    ],
    "temperature": 0.7
  }'
```

### Python Client Example

```python
import requests

response = requests.post(
    "http://localhost:8002/v1/chat/completions",
    json={
        "model": "csdl-14b",
        "messages": [
            {"role": "system", "content": "You are a CSDL-native AI..."},
            {"role": "user", "content": "Create a JWT authentication function"}
        ],
        "temperature": 0.7
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

## Integration with E3-DevMind-AI

The server runs on port 8002, which matches the E3-DevMind-AI configuration in the setup script.

To integrate with E3-DevMind-AI, update the `.env` file:

```bash
# In /opt/e3-devmind-ai/e3-devmind-ai/.env
CSDL_VLLM_URL=http://localhost:8002
VLLM_MODEL=csdl-14b
```

## Performance

With Grace Blackwell's 128GB unified memory:
- **F16 model size**: ~28GB (fits entirely in GPU memory)
- **Inference speed**: Very fast (all layers on GPU)
- **Context window**: 4096 tokens (can be increased if needed)

## Troubleshooting

### Model Not Found Error
```
Error: Model not found: /home/bodhifreeman/E3/E3/csdl-14b-f16.gguf
```
**Solution**: Run `./convert-csdl-to-gguf.sh` first to convert the model.

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Either stop the existing process or change the port in `start-llama-server.sh`.

### Out of Memory
```
CUDA error: out of memory
```
**Solution**: This shouldn't happen with 128GB RAM. Close other GPU applications or reduce `-ngl` parameter.

## Files

- `/home/bodhifreeman/E3/csdl-14b/model/merged_16bit/` - SafeTensors model (source)
- `/home/bodhifreeman/E3/E3/csdl-14b-f16.gguf` - GGUF model (converted)
- `/home/bodhifreeman/E3/E3/llama.cpp/` - llama.cpp source and build
- `/home/bodhifreeman/E3/E3/convert-csdl-to-gguf.sh` - Conversion script
- `/home/bodhifreeman/E3/E3/start-llama-server.sh` - Server startup script

## Next Steps

1. Wait for model copy to complete (monitor with `watch du -sh /home/bodhifreeman/E3/csdl-14b/model/merged_16bit/`)
2. Run conversion script
3. Start llama-server
4. Test with E3-DevMind-AI's 36 agents

## Resources

- CSDL Protocol: `/home/bodhifreeman/E3/E3/csdl-14b/docs/CSDL_PROTOCOL.md`
- Training Info: `/home/bodhifreeman/E3/E3/csdl-14b/docs/TRAINING.md`
- Installation Guide: `/home/bodhifreeman/E3/E3/csdl-14b/docs/INSTALLATION.md`
