# Training Documentation

This document details the training process used to create CSDL-14B, including data preparation, training configuration, and reproduction instructions.

## Table of Contents

1. [Training Overview](#training-overview)
2. [Hardware Used](#hardware-used)
3. [Base Model](#base-model)
4. [Training Data](#training-data)
5. [Phase 1: Base CSDL Training](#phase-1-base-csdl-training)
6. [Phase 2: Atlas LoRA (Reasoning)](#phase-2-atlas-lora-reasoning)
7. [Phase 3: Marketing LoRA (Content)](#phase-3-marketing-lora-content)
8. [Phase 4: NEXUS LoRA (Coding)](#phase-4-nexus-lora-coding)
9. [Hyperparameters](#hyperparameters)
10. [Reproducing Training](#reproducing-training)

## Training Overview

CSDL-14B was trained in four phases:

| Phase | Type | Purpose | Duration |
|-------|------|---------|----------|
| 1 | Full fine-tune + LoRA merge | Base CSDL understanding | ~20 hours |
| 2 | LoRA adapter | Reasoning specialization | ~3 hours |
| 3 | LoRA adapter | Content generation | ~2 hours |
| 4 | LoRA adapter | Code generation | ~6 hours |

**Total training time**: ~31 hours

## Hardware Used

- **System**: NVIDIA DGX Spark
- **GPU**: NVIDIA GB110 (Blackwell architecture)
- **VRAM**: 128 GB unified memory
- **Framework**: Unsloth + Transformers + TRL

## Base Model

- **Model**: [Qwen2.5-14B-Instruct](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)
- **Parameters**: 14.7 billion
- **Architecture**: Qwen2 (similar to Llama)
- **Context Length**: 131,072 tokens (native), 4,096 used for training
- **License**: Qwen License

### Why Qwen2.5-14B?

1. **Strong instruction following**: Pre-trained for instruction tasks
2. **Excellent JSON output**: Good at structured generation
3. **Reasonable size**: Balance of capability and efficiency
4. **Long context**: Supports extended conversations
5. **Open weights**: Available for fine-tuning

## Training Data

### Data Sources

Training data was synthetically generated using patterns from:

- Agent framework implementations (LangChain, AutoGen, CrewAI)
- Tool use patterns and RAG systems
- Memory management strategies
- Multi-agent coordination protocols
- Code generation examples

### Data Statistics

| Category | Examples | Percentage |
|----------|----------|------------|
| Agent patterns | 8,500 | 26.5% |
| Workflow patterns | 6,200 | 19.4% |
| Code patterns | 7,800 | 24.4% |
| Memory patterns | 4,100 | 12.8% |
| Self-reflection | 3,200 | 10.0% |
| Multi-agent | 2,200 | 6.9% |
| **Total** | **32,000** | **100%** |

### Data Format

All training examples follow the ChatML format:

```
<|im_start|>system
You are a CSDL-native AI assistant...<|im_end|>
<|im_start|>user
{instruction}<|im_end|>
<|im_start|>assistant
{csdl_json_output}<|im_end|>
```

## Phase 1: Base CSDL Training

### Objective

Train the base model to understand and output CSDL format consistently.

### Configuration

```python
# Model settings
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True

# LoRA configuration
LORA_R = 16
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]

# Training settings
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
WARMUP_STEPS = 100
```

### Training Metrics

- **Final Loss**: 0.42
- **Steps**: ~12,000
- **Duration**: ~20 hours

### Post-Training

After Phase 1, the LoRA adapter was merged into the base model to create the final base CSDL model.

## Phase 2: Atlas LoRA (Reasoning)

### Objective

Create a specialized adapter for reasoning, planning, and reflection tasks.

### Data Patterns

| Pattern | Examples |
|---------|----------|
| self_reflection_self_critique | 1,200 |
| self_reflection_strategy_adjustment | 980 |
| self_reflection_experience_replay | 850 |
| workflow_planning | 1,100 |
| workflow_multi_step | 890 |
| workflow_autonomous_loop | 720 |
| memory_* | 859 |
| **Total** | **6,599** |

### Configuration

```python
LORA_R = 32  # Higher rank for reasoning complexity
LORA_ALPHA = 32
LEARNING_RATE = 1e-4
NUM_EPOCHS = 2
```

### Training Metrics

- **Final Loss**: 0.38
- **Steps**: ~820
- **Duration**: ~3 hours

## Phase 3: Marketing LoRA (Content)

### Objective

Create a specialized adapter for content generation and skill orchestration.

### Data Patterns

| Pattern | Examples |
|---------|----------|
| csdl_compression | 1,450 |
| skills_skill_composition | 1,120 |
| skills_deterministic_execution | 980 |
| skills_skill_definition | 890 |
| rag_simple_rag | 760 |
| function_generation | 680 |
| multiagent_* | 584 |
| **Total** | **6,464** |

### Configuration

```python
LORA_R = 16  # Standard rank for content
LORA_ALPHA = 16
LEARNING_RATE = 1e-4
NUM_EPOCHS = 2
```

### Training Metrics

- **Final Loss**: 0.35
- **Steps**: ~800
- **Duration**: ~2 hours

## Phase 4: NEXUS LoRA (Coding)

### Objective

Create a specialized adapter for code generation and tool implementation.

### Data Patterns

| Pattern | Examples |
|---------|----------|
| function_retrieval | 2,800 |
| function_agent | 2,450 |
| function_execute | 2,100 |
| function_generation | 3,200 |
| function_memory | 1,950 |
| class_agent | 2,100 |
| class_tool | 1,850 |
| class_rag | 1,420 |
| error_handling | 1,637 |
| **Total** | **19,507** |

### Configuration

```python
LORA_R = 32  # Higher rank for code complexity
LORA_ALPHA = 32
LEARNING_RATE = 1e-4
NUM_EPOCHS = 2
```

### Training Metrics

- **Final Loss**: 0.31
- **Steps**: ~2,440
- **Duration**: ~6 hours

## Hyperparameters

### Common Settings

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW 8-bit |
| Weight Decay | 0.01 |
| LR Scheduler | Cosine |
| Max Grad Norm | 1.0 |
| FP16/BF16 | BF16 (when supported) |
| Gradient Checkpointing | Enabled |

### Training Arguments

```python
TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    learning_rate=2e-4,  # Phase 1
    # learning_rate=1e-4,  # Phases 2-4
    fp16=False,
    bf16=True,
    logging_steps=25,
    save_strategy="steps",
    save_steps=500,
    eval_strategy="steps",
    eval_steps=500,
    load_best_model_at_end=True,
    optim="adamw_8bit",
    seed=42,
)
```

## Reproducing Training

### Requirements

```bash
pip install unsloth
pip install transformers>=4.36.0
pip install trl>=0.7.0
pip install datasets
pip install peft
pip install bitsandbytes
```

### Training Script Structure

```
scripts/
├── train_phase1_base.py      # Base CSDL training
├── train_phase2_atlas.py     # Reasoning LoRA
├── train_phase3_marketing.py # Content LoRA
├── train_phase4_nexus.py     # Coding LoRA
└── export_gguf.sh            # Export to GGUF
```

### Running Training

```bash
# Phase 1 - Base model (~20 hours)
python scripts/train_phase1_base.py

# Phase 2-4 - LoRA adapters (~11 hours)
python scripts/train_phase2_atlas.py
python scripts/train_phase3_marketing.py
python scripts/train_phase4_nexus.py

# Export to GGUF
./scripts/export_gguf.sh
```

### Expected Output

```
models/
├── phase1_base_csdl/
│   └── final_merged/          # Merged base model
├── phase2_reasoning_atlas/
│   └── atlas_lora/            # LoRA adapter
├── phase3_content_marketing/
│   └── marketing_lora/        # LoRA adapter
└── phase4_coder_nexus/
    └── nexus_lora/            # LoRA adapter
```

## Model Export

### GGUF Conversion

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build

# Convert to FP16 GGUF
python convert_hf_to_gguf.py \
    /path/to/final_merged \
    --outfile csdl-14b-f16.gguf \
    --outtype f16

# Quantize to Q4_K_M
./build/bin/llama-quantize \
    csdl-14b-f16.gguf \
    csdl-14b-q4_k_m.gguf \
    Q4_K_M
```

### Quantization Options

| Quantization | Size | Quality | Speed |
|--------------|------|---------|-------|
| F16 | 28 GB | Best | Slowest |
| Q8_0 | 14 GB | Excellent | Fast |
| Q6_K | 11 GB | Very Good | Faster |
| Q5_K_M | 10 GB | Good | Fast |
| Q4_K_M | 8.4 GB | Good | Fastest |
| Q4_K_S | 8.0 GB | Acceptable | Fastest |

---

For questions about training, please [open an issue](https://github.com/LUBTFY/csdl-14b/issues).
