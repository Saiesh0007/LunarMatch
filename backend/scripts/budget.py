"""Budget tracker script.

Reads the most recent match_decisions.jsonl and reports cumulative
stage timings against a 20,000 ms budget constraint.
"""
import json
import sys
from pathlib import Path

def main():
    outputs_dir = Path(r"c:\lm\lm\backend\outputs")
    if not outputs_dir.exists():
        print("No outputs directory found.")
        return
        
    runs = sorted([d for d in outputs_dir.iterdir() if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)
    if not runs:
        print("No pipeline runs found.")
        return
        
    if len(sys.argv) > 1:
        latest_run = Path(sys.argv[1])
    else:
        latest_run = runs[0]
    jsonl = latest_run / "match_decisions.jsonl"
    
    if not jsonl.exists():
        print(f"No match_decisions.jsonl in {latest_run.name}")
        return
        
    # Check fixture shape from input_metadata.json if present
    meta_json = latest_run / "input_metadata.json"
    dim_str = "unknown"
    if meta_json.exists():
        try:
            with open(meta_json, "r", encoding="utf-8") as f_meta:
                mdata = json.load(f_meta)
                dim_str = f"{mdata.get('reference_dimensions', ['?','?'])[0]}x{mdata.get('reference_dimensions', ['?','?'])[1]}"
        except Exception:
            pass

    BUDGET_MS = 20000.0
    cumulative = 0.0
    
    print(f"Budget Report for: {latest_run.name} (Fixture shape: {dim_str})")
    print(f"{'Stage':<20} {'ms':<10} {'Cumulative':<15} {'Budget headroom':<15}")
    print("-" * 65)
    
    with open(jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except:
                continue
                
            if "stage" in entry and "ms" in entry:
                ms = entry["ms"]
                cumulative += ms
                headroom = BUDGET_MS - cumulative
                print(f"{entry['stage']:<20} {ms:<10.1f} {cumulative:<15.1f} {headroom:<15.1f}")
                
    print("-" * 65)
    
    percent = (cumulative / BUDGET_MS) * 100
    print(f"Total time: {cumulative:.1f} ms ({percent:.1f}% of budget)")

if __name__ == "__main__":
    main()
