# check_jsonl_length.py
from pathlib import Path


def count_rows(path):
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())  # skip blank lines

#files with errors are listed in the errors.log to be excluded
excluded_list = ["result_235B_lawnet_91.jsonl", "result_235B_lawnet_92.jsonl", "result_235B_lawnet_64.jsonl"]

#set folder paths
result_dir = Path('/workspace/alfred/vllm/results/new-Qwen3-235B')
new_masked_dir = Path('/workspace/alfred/vllm/data/new_masked')
masked_dir = Path('/workspace/alfred/vllm/data/masked')
temp_dir = Path('/workspace/alfred/vllm/data/temp')
cleaned_dir = Path('/workspace/alfred/vllm/data/cleaned')
counter = 0

#loop through each jsonl file and count & compare the number of rows
for result_file_path in result_dir.rglob("*.jsonl"):
    counter+=1
    filename = result_file_path.stem.replace('result_235B_','')
    masked_path = masked_dir/f"{filename}.jsonl"
    cleaned_path = cleaned_dir/f"{filename}.jsonl"

    #if result_file_path.name in excluded_list: continue

    count1 = count_rows(result_file_path)
    count2 = count_rows(cleaned_path)
    

    #Compare the counters
    if count1 == count2:
        print(f"✅ Both files for {filename} have the same length.")
    else:
        print(f"❌ Files for {filename} have different lengths.")



print(f"Total files: {counter}")

