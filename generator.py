import time 
from helpers import prompt_response, split_thinking_and_main_content, log_to_jsonl, extract_text_from_html 
from config import input_dir, result_dir_235B, generator_error_path 
from templates.generator import GENERATOR_TEMPLATE, GENERATOR_FORMAT 
import json 
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor 
import threading

thread_lock = threading.Lock()

def run_generator(jsonl_file:Path):
    """Process the JSONL file here"""

    start_time = time.time()

    output_file = result_dir_235B / f"result_235B_{jsonl_file.name}"

    #skipped if the output file exist
    if output_file.exists():
        print(f"[Skipping] {output_file.name}")
        return output_file

    print(f"[Processing] {jsonl_file.name}")

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            #skip empty lines
            if not line.strip(): continue

            for attempt in range(3):
                try:
                    #parse JSON line
                    obj = json.loads(line)
                    raw_html = obj["data"]["document"]
                    chunk_content = extract_text_from_html(raw_html)

                    #build prompt
                    prompt = GENERATOR_TEMPLATE.format(GENERATOR_FORMAT=GENERATOR_FORMAT, chunk_content=chunk_content)

                    print(f"[{jsonl_file.name}] LLM is generating...")
                    
                    #Generate synthetic output
                    content = prompt_response(prompt)
                    result = split_thinking_and_main_content(content, prompt)

                    log_to_jsonl(output_file, result)
                    #exit the retry loop
                    break
                except Exception as e:
                    #record error after 3 attempts
                    if attempt == 2:
                        rec = {
                            "file": jsonl_file.name,
                            "line": line_no,
                            "error_message": str(e)
                        }

                        with thread_lock:
                            log_to_jsonl(generator_error_path, rec)
                    continue

    end_time = time.time()
    print(f"[{jsonl_file.name}]Execution time: {end_time - start_time: .4f} seconds") 
    return output_file



def main(): 
    jsonl_files = [jsonl_file for jsonl_file in input_dir.glob("*.jsonl")]
    #process for all the jsonl files in the new_masked folder 
    # for jsonl_file in input_dir.glob("*.jsonl"):
    #     if jsonl_file.name == "lawnet_30.jsonl":
    #         run_generator(jsonl_file)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures= [executor.submit(run_generator,f) for f in jsonl_files]

if __name__ == "__main__": 
    main()