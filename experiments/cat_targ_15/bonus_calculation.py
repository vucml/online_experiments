
"""
extract_bonus.py — **hard-coded paths**

Reads one .jsonl export (each line = one participant) and writes a two-column
CSV with Prolific IDs and bonuses. 
"""

import csv
import json
import re
from pathlib import Path

# Set in and out paths
IN_FILE  = Path("/Users/roberttornatore/Desktop/JATOS/study_assets_root/online_experiments/experiments/cat_targ_15/06_17_2025.jsonl")
OUT_FILE = Path("/Users/roberttornatore/Desktop/JATOS/study_assets_root/online_experiments/experiments/cat_targ_15/bonuses.csv")

# Set keys to find prolific ID and bonus
ID_KEY     = ["PROLIFIC ID"]
BONUS_KEY  = ["bonus"]

def extract_pairs(jsonl_path):
    """Return a list of (prolific_id, bonus) tuples."""
    pairs = []

    with jsonl_path.open("r", encoding="utf-8") as fh:
        # for each line in file
        for line in fh:
            if not line.strip():
                continue  # skip blanks
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # bad JSON → ignore

            records = entry if isinstance(entry, list) else [entry]
            pid = bonus = None
            # for each record
            for rec in records:
                # ID
                if pid is None:
                    for k in ID_KEY:
                        if k in rec:
                            pid = str(rec[k])
                            break
                # Bonus field
                if bonus is None:
                    for k in BONUS_KEY:
                        if k in rec:
                            try:
                                bonus = float(rec[k])
                            except (TypeError, ValueError):
                                pass
                            break

            if pid and bonus is not None:
                pairs.append((pid, bonus))
    return pairs


def export_csv(rows, csv_path):
    """Write list of tuples to CSV."""
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["prolific_id", "bonus"])
        writer.writerows(rows)


if __name__ == "__main__":
    if not IN_FILE.exists():
        raise FileNotFoundError(f"Input not found: {IN_FILE}")

    rows = extract_pairs(IN_FILE)
    export_csv(rows, OUT_FILE)
