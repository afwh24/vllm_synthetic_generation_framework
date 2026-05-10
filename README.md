# vLLM Synthetic Data Generation Framework

A scalable synthetic data generation and evaluation framework built on vLLM for large-scale structured dataset creation using modern open-source large language models.

---

## Overview

This project provides an end-to-end framework for:
- Hosting large language models with vLLM
- Generating structured synthetic datasets
- Running automated evaluation pipelines
- Producing JSON-formatted outputs for downstream AI workflows

The framework supports high-throughput inference using multi-GPU deployments and OpenAI-compatible APIs.

---

## Features

### vLLM Inference Hosting
- OpenAI-compatible API server
- Multi-GPU tensor parallelism
- Long-context inference support
- High-throughput generation

### Synthetic Data Generation
- Structured prompting pipelines
- JSON-formatted outputs
- Reasoning-aware generation
- Domain-specific prompt templates

### Automated Evaluation Pipeline
- PASS/FAIL validation
- Hallucination detection
- Information leakage checking
- Semantic consistency evaluation

### Dataset Management
- JSONL dataset outputs
- Batch processing workflows
- Error logging
- Statistical result aggregation

---

## Pipeline Architecture

1. Host models using vLLM
2. Generate structured synthetic outputs
3. Run evaluation/checker pipeline
4. Validate generated responses
5. Aggregate evaluation statistics
6. Store outputs into JSONL datasets

---

## Supported Models

Examples include:
- Qwen3-32B
- Qwen3-235B
- OpenAI-compatible models

---

## Example Server Launch

```bash
vllm serve /path/to/model \
  --host 0.0.0.0 \
  --port 8001 \
  --tensor-parallel-size 8
```

---

## Example API Usage

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="no-key-needed"
)

response = client.chat.completions.create(
    model="Qwen3-32B",
    messages=[
        {"role": "user", "content": "Generate synthetic data"}
    ]
)
```

---

## Dataset Schema

Example output:

```json
{
  "prompt": "...",
  "thinking_content": "...",
  "main_content": {
    "overview": "...",
    "reasoning": "...",
    "conclusion": "...",
    "confidence": 0.95
  }
}
```

---

## Technologies Used

- Python
- vLLM
- Transformers
- OpenAI-compatible APIs
- Multi-GPU inference
- JSONL

---

## Usage

### Start vLLM Server

```bash
python main.py
```

### Run Generation Pipeline

```bash
python generator.py
```

### Run Evaluation Pipeline

```bash
python checker.py
```

---

## Project Structure

```text
vllm_framework/
├── prompts/
├── results/
├── logs/
├── scripts/
├── generator.py
├── checker.py
└── README.md
```

---

## Applications

- Synthetic dataset generation
- LLM evaluation
- Legal AI workflows
- Instruction tuning
- Benchmark creation

---

## Scalability

The framework supports:
- Multi-GPU inference
- Long-context reasoning
- High-throughput generation
- Large-scale dataset production

---

## Future Improvements

- Distributed inference scheduling
- Automatic prompt optimization
- Multi-model ensemble generation
- Advanced reasoning verification
