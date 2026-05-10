import time
from helpers import prompt_response, split_thinking_and_main_content, log_to_jsonl, extract_text_from_html
from config import result_dir_235B, checker_error_path, checker_dir, cleaned_dir, temp_dir, generator_error_path
from templates.checker import CHECKER_TEMPLATE, CHECKER_FORMAT
import json
import shutil
from itertools import zip_longest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor 
import threading

thread_lock = threading.Lock()


#read the generator error log and store the file name and lines into a dictionary
def read_error_logs(error_log):
    error_map = {}
    with open(error_log, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            filename = obj['file']
            line_no = obj['line']
            error_map.setdefault(filename, set()).add(line_no)

    return error_map

#process each file with errors and update them into a temp dir
def remove_error_lines_from_files(error_log):
    #remove existing temp dir
    if temp_dir.exists(): shutil.rmtree(temp_dir)
    
    #create new temp dir to store the updated jsonl files
    temp_dir.mkdir(parents=True, exist_ok=True)

    files_with_error = read_error_logs(error_log)

    for filename in files_with_error:
        cleaned_file = cleaned_dir/filename
        temp_file = temp_dir/filename

        skip_lines = files_with_error.get(filename,set())
        print(f"[Updating] {filename}")
        #process the clean file and save it into the temp dir
        with open(cleaned_file, "r", encoding="utf-8") as f_in, \
             open(temp_file, "w", encoding="utf-8") as f_out:
            for line_no, line in enumerate(f_in, start=1):
                if not line.strip(): continue

                if line_no in skip_lines:
                    print(f"[{filename}] Skipping line {line_no}")
                    continue
                
                f_out.write(line)


#checker - to compare the original conclusion and synthetic generated conclusion
def checker(original:str, synthetic:dict):
    """
    Compare the original conclusion and synthetic generated conclusion
    using the checker prompt and return the parsed LLM result.
    """
    #get the synthetic conclusion
    synthetic_conclusion = synthetic["main_content"]["conclusion"]
    checker_prompt = CHECKER_TEMPLATE.format(original_result = original, synthetic_result = synthetic_conclusion, CHECKER_FORMAT = CHECKER_FORMAT)
    #get the LLM to compare the original and synthetic conclusion
    checker_response = prompt_response(checker_prompt)
    return split_thinking_and_main_content(checker_response, checker_prompt)

def run_checker(jsonl_file:Path):
    """
    Run the checker for a single result_235B_*.jsonl file.
    Reads the corresponding cleaned file and writes checker output.
    """
    #basic set up
    start_time = time.time()
    base_name = jsonl_file.name.replace("result_235B_","")
    checker_file = checker_dir/f"checker_{base_name}"
    cleaned_file = cleaned_dir/base_name
    temp_file = temp_dir/base_name

    #if temp file exist -> there is an error during generation
    if temp_file.exists():
        cleaned_file = temp_file

    #skip if checker file exists
    if checker_file.exists():
        print(f"[Skipping] {checker_file.name}")
        return
    
    print(f"[Checking] {jsonl_file.name}")

    with open(jsonl_file, "r", encoding="utf-8") as file_synthetic,\
         open(cleaned_file, "r", encoding="utf-8") as file_original:
        
        for line_no, (synthetic_line, original_line) in enumerate(zip_longest(file_synthetic, file_original, fillvalue=""), start=1):


            #skip if both lines are empty
            if not synthetic_line.strip() and not original_line.strip(): continue

            #if either one is empty skip also or can log the error here
            if not synthetic_line.strip() or not original_line.strip(): continue

            for attempt in range(3):
                try:
                    #Parse both JSON objects
                    synthetic_obj = json.loads(synthetic_line)
                    original_obj = json.loads(original_line)

                    #extract original text from html
                    raw_html = original_obj["data"]["document"]
                    original_text = extract_text_from_html(raw_html)

                    #Call checker model
                    print(f"[Checking]LLM is checking... (file={jsonl_file.name}, line={line_no})")
                    result = checker(original_text, synthetic_obj)

                    #empty result
                    if result is None: continue 
                    
                    log_to_jsonl(checker_file, result)
                    break #exit the retry loop


                except Exception as e:
                    if attempt == 2:
                        #Record errors into the checker error log
                        rec = {
                            "file": jsonl_file.name,
                            "line": line_no,
                            "error_message": str(e)
                        }
                        with thread_lock:
                            log_to_jsonl(checker_error_path, rec)

                    continue
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time: .4f} seconds")




def main():
    #Run cleaning step first
    remove_error_lines_from_files(generator_error_path)

    result_files = [result_file for result_file in result_dir_235B.glob("*.jsonl")]

    #execute the checker with 5 thread workers
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures= [executor.submit(run_checker,f) for f in result_files]

if __name__ == "__main__":
    main()

