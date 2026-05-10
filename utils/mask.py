import json
from pathlib import Path
from bs4 import BeautifulSoup, Tag

#script to mask the conclusion of the original file output

# Only exact matches (case-insensitive) will trigger removal
KEYWORDS = { "conclusion", "judgment", "judgement", "decision", "orders", "order", "outcome", "result", "holding", "summary", "in summary", "in conclusion", "my decision" }

def normalize_heading_text(t: str) -> str:
    # exact word match: trim, lowercase, drop a trailing colon if present
    t = (t or "").strip().lower()
    if t.endswith(":"):
        t = t[:-1].rstrip()
    return t

def remove_from_heading_onward(html: str) -> str:
    if not isinstance(html, str) or not html.strip():
        return html
    soup = BeautifulSoup(html, "html.parser")

    for h in soup.select('[class^="Judg-Heading-"]'):   # any tag with this class
        txt = normalize_heading_text(h.get_text(" ", strip=True))
        if txt in KEYWORDS:                    # <-- exact match only
            cur = h
            while cur is not None:
                nxt = cur.next_sibling
                try: cur.extract()
                except Exception:
                    if isinstance(cur, Tag):
                        cur.decompose()
                cur = nxt
            break
    return str(soup)

def process_jsonl(in_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{in_path.stem}.jsonl"
    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip(): 
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            data = obj.get("data", {})
            doc = data.get("document")
            if isinstance(doc, str) and doc:
                data["document"] = remove_from_heading_onward(doc)
                obj["data"] = data
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print("Wrote:", out_path)

if __name__ == "__main__":
    cleaned_dir = Path("/workspace/alfred/vllm/data/cleaned")
    masked_dir = Path("/workspace/alfred/vllm/data/new_masked")
    for jsonl_file in cleaned_dir.rglob("*.jsonl"):
        print(f"Masking: {jsonl_file.name}")
        process_jsonl(jsonl_file, masked_dir)

