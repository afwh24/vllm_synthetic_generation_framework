import json
from config import cleaned_dir, temp_dir, generator_error_path
import shutil
from concurrent.futures import ThreadPoolExecutor 
from checker import run_checker

#simple script to create a temp file to store the files with problem during generation stage

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


def main():
    remove_error_lines_from_files(generator_error_path)
    temp_files = [temp_file for temp_file in temp_dir.glob("*.jsonl")]

    print(len(temp_files))

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures= [executor.submit(run_checker,f) for f in temp_files]

if __name__ == "__main__": 
    main()
