import json
from pathlib import Path
from config import checker_pass_dir, checker_fail_dir, checker_dir
import shutil

MAX_LINES_PER_FILE = 100  # cap per output file

#delete and create checker_pass_dir and checker_fail_dir if they exist
def reset_checker_dir():
    if checker_pass_dir.exists():
        shutil.rmtree(checker_pass_dir)
    if checker_fail_dir.exists():
        shutil.rmtree(checker_fail_dir)

    checker_pass_dir.mkdir(parents=True, exist_ok=True)
    checker_fail_dir.mkdir(parents=True, exist_ok=True)

#sort the pass and fail results into their corresponding directories
def main():
    reset_checker_dir()
    print(f"Reading from {checker_dir}")

    pass_total = 0
    fail_total = 0

    # PASS file state
    pass_idx = 1
    pass_lines = 0
    f_pass = open(checker_pass_dir / f"checker_pass_{pass_idx}.jsonl", "w", encoding="utf-8")

    # FAIL file state
    fail_idx = 1
    fail_lines = 0
    f_fail = open(checker_fail_dir / f"checker_fail_{fail_idx}.jsonl", "w", encoding="utf-8")

    try:
        for jsonl_file in checker_dir.glob("*.jsonl"):
            with open(jsonl_file, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    if not line.strip():
                        continue

                    try:
                        obj = json.loads(line)
                        main_content = obj.get("main_content", {})
                        verdict = main_content.get("overall_verdict")
                    except Exception as e:
                        print(f"Error parsing line in {jsonl_file.name}: {e}")
                        continue

                    if verdict == "PASS":
                        if pass_lines >= MAX_LINES_PER_FILE:
                            f_pass.close()
                            pass_idx += 1
                            pass_lines = 0
                            f_pass = open(checker_pass_dir / f"checker_pass_{pass_idx}.jsonl", "w", encoding="utf-8")

                        f_pass.write(line)
                        pass_lines += 1
                        pass_total += 1

                    elif verdict == "FAIL":
                        if fail_lines >= MAX_LINES_PER_FILE:
                            f_fail.close()
                            fail_idx += 1
                            fail_lines = 0
                            f_fail = open(checker_fail_dir / f"checker_fail_{fail_idx}.jsonl", "w", encoding="utf-8")

                        f_fail.write(line)
                        fail_lines += 1
                        fail_total += 1

    finally:
        f_pass.close()
        f_fail.close()

    print(f"Done. Total PASS: {pass_total}, total FAIL: {fail_total}")
    print(f"PASS JSONL files: {pass_idx}")
    print(f"FAIL JSONL files: {fail_idx}")


if __name__ == "__main__":
    main()
