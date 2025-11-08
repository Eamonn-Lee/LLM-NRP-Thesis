#!/usr/bin/env python3
# run_all_metrics_in_order.py
#
# Strictly preserve a deterministic file order when running:
#   recency.py, role.py, firstfit.py
# on every *.json in --dir (recursing into subfolders).
#
# Order rule: natural, case-insensitive sort by *relative path* from --dir.
# (e.g., file2.json comes before file10.json).
#
# Usage:
#   python3 run.py --dir ./files --out-prefix results 

import argparse
import os
import subprocess
import sys
from typing import List

def natural_key(s: str):
    """Case-insensitive natural sort key for paths (numbers sort numerically)."""
    import re
    s_lower = s.lower()
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', s_lower)]

def gather_json_files_in_order(root_dir: str) -> List[str]:
    # Collect all .json paths with their relative paths
    paths = []
    root_dir = os.path.abspath(root_dir)
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().endswith(".json"):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root_dir)
                paths.append((rel, full))
    # Sort by natural key of the relative path to make order deterministic
    paths.sort(key=lambda t: natural_key(t[0]))
    return [full for _rel, full in paths]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="Directory containing JSON files (recursed)")
    ap.add_argument("--out-prefix", default="results", help="Prefix for output text files")

    ap.add_argument("--recency-script", default="recency.py", help="Path to recency script")
    ap.add_argument("--role-script", default="role.py", help="Path to role anchoring script")
    ap.add_argument("--firstfit-script", default="firstfit.py", help="Path to first-fit bias script")
    args = ap.parse_args()

    json_files = gather_json_files_in_order(args.dir)

    if not json_files:
        print("No JSON files found.", file=sys.stderr)
        return

    py = sys.executable or "python3"

    with open(f"{args.out_prefix}_recency_bias.txt", "w", encoding="utf-8") as recency_out, \
         open(f"{args.out_prefix}_role_anchoring.txt", "w", encoding="utf-8") as role_out, \
         open(f"{args.out_prefix}_first_fit_bias.txt", "w", encoding="utf-8") as firstfit_out:

        for json_file in json_files:
            print(f"Processing {json_file}...")

            # Recency bias (preserve execution & write order)
            rec = subprocess.run(
                [py, args.recency_script, "--json", json_file],
                text=True, capture_output=True
            )
            recency_out.write(f"=== {json_file} ===\n{rec.stdout}\n")
            recency_out.flush()

            # Role anchoring
            role = subprocess.run(
                [py, args.role_script, "--json", json_file],
                text=True, capture_output=True
            )
            role_out.write(f"=== {json_file} ===\n{role.stdout}\n")
            role_out.flush()

            # First-fit bias
            ff = subprocess.run(
                [py, args.firstfit_script, "--json", json_file],
                text=True, capture_output=True
            )
            firstfit_out.write(f"=== {json_file} ===\n{ff.stdout}\n")
            firstfit_out.flush()

    print("Done. Outputs written in deterministic (natural path) order.")

if __name__ == "__main__":
    main()
