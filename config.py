from pathlib import Path

#dir path
input_dir = Path("/workspace/alfred/vllm/data/masked")
cleaned_dir = Path("/workspace/alfred/vllm/data/cleaned")
results_dir = Path("/workspace/alfred/vllm/results")

result_dir_235B = Path("/workspace/alfred/vllm/results/Qwen3-235B")
checker_dir = Path("/workspace/alfred/vllm/results/checker")

#these folders will be created only when split_checker_results.py is being executed
checker_pass_dir = results_dir / "checker_pass"
checker_fail_dir = results_dir / "checker_fail"

#temp_dir only consist of the cleaned input data (with error lines removed based on the generator log)
temp_dir = Path("/workspace/alfred/vllm/data/temp")

#error path
generator_error_path = Path("/workspace/alfred/vllm/logs/generator_log.jsonl") 
checker_error_path = Path("/workspace/alfred/vllm/logs/checker_log.jsonl")

result_dir_235B.mkdir(parents=True, exist_ok=True)
checker_dir.mkdir(parents=True, exist_ok=True)

#LLM configuration (for VLLM serve)
model = "/workspace/alfred/vllm/models/Qwen3-235B-A22B-Thinking-2507/"
base_url = "http://localhost:8001/v1"
max_tokens= 20000


