# PyTorch CUDA Build Guide for DGX Spark

## Why We're Building from Source

The pre-built PyTorch wheels don't support:
- ARM64 architecture (Grace CPU)
- Blackwell GPU (compute capability 12.1)

Building from source gives us:
- ✅ Full CUDA 13.0 support
- ✅ Blackwell GB10 optimization
- ✅ ARM64 NEON SIMD acceleration
- ✅ Maximum inference performance

## Build Process

### Step 1: Start the Build
```bash
cd /home/bodhifreeman/E3/E3
./build-pytorch-cuda.sh
```

**Expected time:** 2-4 hours (make coffee, take a walk, pet a dog)

### Step 2: Monitor Progress
```bash
tail -f /tmp/pytorch-build.log
```

### Step 3: After Build Completes

Activate the environment:
```bash
source /home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate
```

Install additional dependencies:
```bash
pip install transformers accelerate fastapi uvicorn
```

### Step 4: Update CSDL Server

Edit `csdl-server.py` to use GPU again:
```python
# Change this:
device_map="cpu"

# To this:
device_map="cuda:0"
torch_dtype=torch.bfloat16
```

### Step 5: Test It

```bash
# Start CSDL server
python3 csdl-server.py

# In another terminal, test:
curl -s http://localhost:8003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {"role": "system", "content": "You are CSDL-14B. Compress to CSDL Structured format using T, C, R fields."},
      {"role": "user", "content": "Compress: Build a JWT authentication system"}
    ],
    "max_tokens": 150,
    "temperature": 0.1
  }'
```

## Expected Output

**Good CSDL output:**
```json
{"T": "auth", "C": [{"id": "jwt"}], "cx": 0.8}
```

**NOT garbage with Chinese characters!**

## Performance Expectations

With properly built PyTorch + CUDA:
- **Inference speed:** 15-25 tokens/second (Grace Blackwell)
- **Model loading:** ~30 seconds (28GB FP16)
- **Memory usage:** ~32GB VRAM
- **Quality:** Perfect tokenization, no corruption

## Troubleshooting

### Build fails with CUDA errors
```bash
# Check CUDA version
nvcc --version

# Should show: release 13.0
```

### Build fails with memory issues
```bash
# Reduce parallel jobs
export MAX_JOBS=8
./build-pytorch-cuda.sh
```

### Build succeeds but torch.cuda.is_available() = False
```bash
# Check CUDA_HOME
echo $CUDA_HOME

# Should be: /usr/local/cuda-13.0
```

## Alternative: Pre-built Wheels (If Available)

If PyTorch eventually releases ARM64+CUDA wheels:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu130
```

But as of January 2026, these don't exist for ARM64.

---

**Rock on!** 🤘
