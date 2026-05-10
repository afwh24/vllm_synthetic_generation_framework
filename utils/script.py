import shutil
import json
from pathlib import Path

#Simple functions to perform certain actions

#simple delete folder script to bypass permission
def deleteFolder(folder_path:Path):
    if folder_path.exists():
        shutil.rmtree(str(folder_path))
        print(f"Folder {folder_path} has been deleted successfully")
    else:
        print(f"Folder {folder_path} does not exist")


#clean raw jsonl file first -> removing those failed data
def clean_raw_jsonl():
    raw_dir = Path("/workspace/alfred/vllm/data/raw")
    cleaned_dir = Path("/workspace/alfred/vllm/data/cleaned")

    for raw_jsonl in raw_dir.glob("*.jsonl"):
        print(f"Cleaning: {raw_jsonl.name}")

        cleaned_file = cleaned_dir/raw_jsonl.name

        with open(raw_jsonl, "r", encoding="utf-8") as fin:
            with open(cleaned_file, "w", encoding="utf-8") as fout:
                for line in fin:
                    if not line.strip(): continue
                    rec = json.loads(line)
                    data = rec["data"]
                    if not data: continue
                    fout.write(json.dumps(rec, ensure_ascii=False) + "\n")


#bypass permission to delete file
def deleteFile(file_path:Path):
    if file_path.exists():
        file_path.unlink()
        print(f"Deleted: {file_path}")

#read jsonl
def read_jsonl(input_jsonl:Path):
    counter = 0
    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            counter+=1
            if not line.strip(): continue
            if counter != 15: continue
            obj = json.loads(line)
            data = obj.get("data", {})
            doc = data.get("document")
            print(doc)
            break

#copy file
def copy_file(src, dest):
    if src.exists():
        shutil.copy(src,dest)
        print(f"File has been copied from {src} to {dest}")

deleteFolder(Path("/workspace/alfred/vllm/data/masked"))

#deleteFile(Path(f"/workspace/alfred/vllm/results/checker/checker_lawnet_103.jsonl"))

