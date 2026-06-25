# LLM Legal Reasoning Evaluation Framework

A synthetic legal reasoning generation and evaluation framework inspired by the Salesforce WebScale-RL pipeline, designed to assess the legal reasoning capabilities of Large Language Models on Singapore court cases.

---

## Overview

This project implements an end-to-end pipeline for generating synthetic legal reasoning outputs using a large language model and systematically evaluating their quality using the same model as an LLM-as-a-Judge evaluator.

The framework was built to assess how effectively LLMs can interpret, reason about, and produce judicial-quality analysis based on Singapore court case materials, with structured evaluation covering reasoning quality, hallucination detection, information leakage, and semantic consistency.

**Source documents:** Singapore court judgments from the [Singapore Judiciary](https://www.judiciary.gov.sg/judgments/judgments-case-summaries)

**Scale:** Approximately 500 synthetic samples generated and evaluated

---

## Pipeline Architecture

### Stage 1 — Synthetic Legal Reasoning Generation
1. Load Singapore court case materials as input context
2. Construct structured prompts for legal reasoning generation
3. Query Qwen3-235B via vLLM inference server to generate synthetic judicial reasoning
4. Parse and validate structured JSON outputs
5. Store generated outputs in JSONL format

### Stage 2 — Automated Evaluation (LLM-as-a-Judge)
1. Load generated synthetic outputs alongside original court case materials
2. Construct evaluation prompts comparing synthetic and original reasoning
3. Query Qwen3-235B as the judge to evaluate each generated output
4. Parse structured evaluation verdicts
5. Aggregate evaluation statistics and log results

---

## Infrastructure

- **Model:** Qwen3-235B (primary model for both generation and evaluation)
- **Inference:** vLLM hosted on 8x 80GB H100 GPUs
- **Parallelism:** Multi-GPU tensor parallelism (tensor-parallel-size 8)
- **API:** OpenAI-compatible API server

---

## Generator Schema

Each synthetic output is structured as follows:

```json
{
  "overview": "Concise summary of the case material, including the parties, nature of the dispute, and the primary legal issues.",
  "reasoning": "Comprehensive judicial reasoning demonstrating how Singapore legal principles are identified, interpreted, and applied to the facts.",
  "conclusion": "Final decision or finding based solely on the given material, expressed in formal judicial language.",
  "confidence": {
    "level": "High | Medium | Low",
    "justification": "One sentence explaining the confidence level based on quality of evidence, clarity of law, and logical certainty."
  }
}
```

**Confidence Level Criteria:**
- **High** — Material is comprehensive and reasoning is strongly supported by clear facts and law
- **Medium** — Material contains some ambiguity or missing information but reasoning remains reasonably justified
- **Low** — Material is insufficient, contradictory, or too incomplete to support a firm conclusion

---

## Checker (Evaluation) Schema

Each evaluation output is structured as follows:

```json
{
  "overall_verdict": "PASS or FAIL",
  "same_meaning": "Y or N",
  "same_meaning_reason": "Explanation referencing both outcome and procedural stage.",
  "info_leakage": "Y or N",
  "info_leakage_reason": "Reference to unusually close phrasing or structure.",
  "hallucination": "Y or N",
  "hallucination_reason": "Justification specifying what was invented or unsupported, if applicable.",
  "conclusion_original": "Exact final conclusion extracted from the original reference.",
  "conclusion_llm": "Exact final conclusion extracted from the synthetic output.",
  "issue_summary": "Summary of issues found, or None if all checks passed."
}
```

**Evaluation Criteria:**
- **Same Meaning** — Whether the synthetic and original judgments reflect the same substantive outcome and procedural stage
- **Information Leakage** — Whether the synthetic output relies on or closely copies the original conclusion wording or unique factual details
- **Hallucination** — Whether the synthetic output introduces facts, charges, reasoning, or legal basis not supported by the original case material
- **Overall Verdict** — PASS if all criteria are acceptable, FAIL otherwise

---

## Technologies Used

- **Language:** Python
- **Model:** Qwen3-235B
- **Inference:** vLLM
- **GPU Infrastructure:** 8x NVIDIA H100 80GB
- **API:** OpenAI-compatible API (via vLLM)
- **Output Format:** JSONL
- **Inspiration:** [Salesforce WebScale-RL Framework](https://github.com/SalesforceAIResearch/PretrainRL-pipeline)
- **Data Source:** [Singapore Judiciary](https://www.judiciary.gov.sg/judgments/judgments-case-summaries)

---

## Applications

- LLM legal reasoning evaluation
- AI benchmarking for legal domain tasks
- Hallucination detection research
- Legal AI dataset quality assessment
- Synthetic legal dataset generation for instruction tuning

---

## Notes

This pipeline was built during an AI Engineer internship at the Home Team Science and Technology Agency (HTX), Singapore. The framework was independently designed and implemented with conceptual inspiration from the Salesforce WebScale-RL pipeline. Source documents and generated datasets are not publicly available.
