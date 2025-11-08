#!/usr/bin/env python3
# role_anchoring.py — tolerant of extra CLI args (ignores unknown flags)

import argparse
import json
import sys
import statistics
from collections import defaultdict

def count_by_field(assignments, field):
    """
    Returns: dict[nurse] -> dict[value_of_field] -> count
    """
    table = defaultdict(lambda: defaultdict(int))
    for a in assignments:
        n = a.get("nurse")
        v = a.get(field)
        if n is None or v is None:
            continue
        table[n][v] += 1
    return table

def print_section(title, table, field_name):
    print(f"=== {title} ===")
    print(f"nurse,{field_name},count")
    for nurse in sorted(table.keys()):
        row = table[nurse]
        for v in sorted(row.keys()):
            print(f"{nurse},{v},{row[v]}")
    print()

def coefficient_of_variation(values, *, population=True):
    """
    CV = std / mean
    - population=True  -> population std dev (denominator n)
    - population=False -> sample std dev (denominator n-1)
    Returns 0.0 if mean is 0 or the list is empty.
    """
    vals = list(values)
    if not vals:
        return 0.0
    mean_val = statistics.mean(vals)
    if mean_val == 0:
        return 0.0
    stdev_val = statistics.pstdev(vals) if population else (
        statistics.stdev(vals) if len(vals) > 1 else 0.0
    )
    return stdev_val / mean_val

def totals_by_category(table):
    """
    table: dict[nurse] -> dict[category_value] -> count
    Returns: dict[category_value] -> total count across all nurses
    """
    totals = defaultdict(int)
    for _nurse, categories in table.items():
        for cat_val, count in categories.items():
            totals[cat_val] += count
    return totals

def cv_by_category(table):
    """
    table: dict[nurse] -> dict[category_value] -> count
    Returns: dict[category_value] -> CV across nurses' counts for that category
    (Only observed nurse-category counts are included.
     If you want to treat missing combos as zeros, you’d need to densify.)
    """
    category_counts = defaultdict(list)  # category_value -> [counts...]
    for _nurse, categories in table.items():
        for cat_val, count in categories.items():
            category_counts[cat_val].append(count)

    results = {}
    for cat_val, counts in category_counts.items():
        results[cat_val] = coefficient_of_variation(counts, population=True)
    return results

def weighted_mean(values, weights):
    num = 0.0
    den = 0.0
    for v, w in zip(values, weights):
        num += v * w
        den += w
    return (num / den) if den else 0.0

def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--json", required=True, help="Path to assignments JSON")
    # Accept and ignore any other flags so this works when called by a generic driver
    args, _unknown = ap.parse_known_args(argv)

    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assignments = data.get("assignments", [])

    # Build cross-tabs
    by_shift = count_by_field(assignments, "shiftType")
    by_skill = count_by_field(assignments, "skill")

    # Keep your original detailed prints
    print_section("Counts by shiftType", by_shift, "shiftType")
    print_section("Counts by skill", by_skill, "skill")

    # Overall CV across nurses (total assignments per nurse)
    total_counts_per_nurse = [sum(nurse_counts.values()) for nurse_counts in by_skill.values()]
    overall_cv = coefficient_of_variation(total_counts_per_nurse, population=True)
    print(f"Aggregated CV (all nurses, all assignments): {overall_cv:.3f}")

    # --- ONE VALUE for shift types ---
    # 1) CV for each shift across nurses
    shift_cvs = cv_by_category(by_shift)
    # 2) Total volume per shift (weights)
    shift_totals = totals_by_category(by_shift)
    # 3) Weighted average CV across all shift types
    #    (so shifts with more assignments contribute proportionally)
    shift_cv_weighted = weighted_mean(
        [shift_cvs[k] for k in shift_cvs.keys()],
        [shift_totals[k] for k in shift_cvs.keys()]
    )
    print(f"CV (shift types, weighted): {shift_cv_weighted:.3f}")

    # --- ONE VALUE for skill types ---
    skill_cvs = cv_by_category(by_skill)
    skill_totals = totals_by_category(by_skill)
    skill_cv_weighted = weighted_mean(
        [skill_cvs[k] for k in skill_cvs.keys()],
        [skill_totals[k] for k in skill_cvs.keys()]
    )
    print(f"CV (skill types, weighted): {skill_cv_weighted:.3f}")

if __name__ == "__main__":
    main(sys.argv[1:])
