# Legal Reasoning Evaluation Framework

An end-to-end pipeline for generating synthetic judicial reasoning from Singapore court cases and evaluating the quality of that reasoning using an LLM-as-a-Judge framework. Built during a six-month AI Engineer internship at HTX, Singapore's national defence-tech agency.

Inspired by [Salesforce's PretrainRL framework](https://github.com/SalesforceAIResearch/PretrainRL-pipeline).

## What this does

Given a real Singapore court judgment, the pipeline:

1. Strips the original judge's conclusion, judgment, decision, and outcome from the source material
2. Prompts a large language model, acting as a Singapore High Court judge, to independently derive its own reasoning and conclusion from the masked case facts
3. Compares the model's synthetic conclusion against the real original conclusion using a second LLM-as-a-Judge pass
4. Produces structured PASS/FAIL verdicts with detailed reasoning across multiple evaluation criteria

The masking step is the core design decision behind this project. By removing the original conclusion before generation, the model has no way to see or copy the real outcome, forcing genuinely independent legal reasoning rather than retrieval.

## Architecture

The pipeline is split into three independently runnable stages, controlled via CLI:

```
python src/main.py --stage generator   # generate synthetic judgments
python src/main.py --stage checker     # evaluate synthetic vs original
python src/main.py --stage split       # split results into pass/fail files
```

### 1. Masking (`mask.py`)
Source judgments are originally HTML. Before generation, headings matching conclusion-related keywords (conclusion, judgment, decision, orders, outcome, holding, summary, etc.) are located, and everything from that heading onward is stripped from the document.

### 2. Generation (`generator.py`)
- Source HTML is parsed to plain text using BeautifulSoup
- A judicial-persona prompt instructs the model to act as a Singapore High Court judge, apply Singapore statutes and case law, and reach an independent conclusion strictly from the masked material
- Model: **Qwen3-235B-A22B-Thinking-2507**, served locally via vLLM with an OpenAI-compatible API
- Because this is a "Thinking" model variant, every response includes a reasoning trace wrapped in `<think>` tags ahead of the structured output. This trace is parsed out and stored separately from the final answer
- Output follows a strict JSON schema: `overview`, `reasoning`, `conclusion`, `confidence` (level + justification)
- Generation is parallelised across a thread pool, with automatic retries on failure and error logging for lines that fail repeatedly

### 3. Checking (`checker.py`)
- Compares the synthetic conclusion against the real, unmasked original conclusion
- The same Qwen3-235B-A22B-Thinking-2507 model acts as the judge
- Evaluation rules are deliberately scoped to avoid penalising reasonable legal inference:
  - **Same meaning**: tolerates minor sentencing differences if proportionate; flags only substantive outcome or procedural-stage mismatches
  - **Hallucination**: flags only genuinely invented facts, evidence, or legal provisions; paraphrasing or inferring the real conclusion from the material is explicitly *not* hallucination
  - **Information leakage**: flags only near-verbatim copying of the original wording; necessary legal references (section numbers, offence names) are explicitly not leakage
- Output is a structured JSON verdict per case: `overall_verdict`, `same_meaning` (+reason), `info_leakage` (+reason), `hallucination` (+reason), `conclusion_original`, `conclusion_llm`, `issue_summary`

### 4. Result analysis (`checker_summary.py`, `split_checker.py`)
- Aggregates Y/N counts per criterion and overall PASS/FAIL totals into a CSV summary
- Splits individual PASS and FAIL records into separate files (capped at 100 records per file) for easier manual review

## Scale

Approximately 500 synthetic legal reasoning samples generated and evaluated.

## What this project does not do

This project does not train or fine-tune any language model. Both generation and evaluation use an existing, pre-deployed Qwen3-235B-A22B-Thinking-2507 inference endpoint served via vLLM. The serving infrastructure itself was set up separately; this codebase is responsible for the generation logic, masking methodology, prompt design, and evaluation framework only.

## Tech stack

Python, vLLM (OpenAI-compatible API), BeautifulSoup, JSON/JSONL, threading (ThreadPoolExecutor)
