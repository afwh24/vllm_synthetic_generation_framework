import json
from pathlib import Path
from config import checker_dir
import csv
import re

FIELDS = ["same_meaning", "info_leakage", "hallucination"]

#analyze the checker file
def analyze_checker_file(file):
    stats = {field: {"Y": 0, "N":0, "total":0} for field in FIELDS}
    overall_stats = {"PASS": 0, "FAIL": 0, "total": 0}

    with open(file, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip(): continue

            obj = json.loads(line)

            #for all the Y/N field
            for field in FIELDS:
                value = obj["main_content"][field]

                stats[field]["total"] +=1
                stats[field][value] += 1
            

            #for overall_verdict only
            verdict = obj["main_content"]["overall_verdict"]
            overall_stats["total"] +=1
            overall_stats[verdict] +=1
    

    return stats, overall_stats

def save_checker_stats_to_csv(source_file, stats, overall_stats, csv_out, write_header=False, fields=FIELDS):
    # build header for a single summary row
    fieldnames = ["file"]  # which checker file this row is summarising

    for field in fields:
        fieldnames.extend([
            f"{field}_Y",
            f"{field}_N",
        ])

    fieldnames.extend([
        "overall_verdict_PASS",
        "overall_verdict_FAIL",
        "total",
    ])

    # build the row for this file
    row = {"file": Path(source_file).name}

    for field in fields:
        y = stats[field]["Y"]
        n = stats[field]["N"]
        # total per field is not stored anymore, only raw counts
        row[f"{field}_Y"] = y
        row[f"{field}_N"] = n

    # overall_verdict
    pass_count = overall_stats["PASS"]
    fail_count = overall_stats["FAIL"]
    total_overall = overall_stats["total"]

    row["overall_verdict_PASS"] = pass_count
    row["overall_verdict_FAIL"] = fail_count
    row["total"] = total_overall  # single total

    # write / append to CSV
    mode = "w" if write_header else "a"

    try:
        # Ensure parent directory exists
        Path(csv_out).parent.mkdir(parents=True, exist_ok=True)

        with open(csv_out, mode, newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=fieldnames, extrasaction='ignore')
            if write_header:
                writer.writeheader()
            writer.writerow(row)
    except IOError as e:
        print(f"Error writing to CSV {csv_out}: {e}")
    except Exception as e:
        print(f"Unexpected error in save_checker_stats_to_csv: {e}")


def main():
    csv_out = "/workspace/alfred/vllm/checker_summary.csv"
    
    files = list(checker_dir.rglob("*.jsonl"))
    files = sorted(files, key=lambda p: int(p.stem.split("_")[-1]))

    for idx, file in enumerate(files):
        stats, overall_stats = analyze_checker_file(file)
        write_header = (idx == 0)  # first file -> write header
        save_checker_stats_to_csv(file, stats, overall_stats, csv_out, write_header=write_header)
main()