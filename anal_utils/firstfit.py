#!/usr/bin/env python3
"""
firstfit

- Nurse order is HARD-CODED in __main__ (as requested).
- Accepts --json <file> to read assignments.
- Computes a single first-fit bias score based on average rank of assigned nurses.
- Keeps outputs/styling compatible with previous parsing (Total assignments, Average rank used | Expected, etc.).
"""

import argparse
import json
from collections import Counter

def extend_order_with_unknowns(assignments, base_order):
    """Append any nurses seen in assignments but missing from base_order, preserving first-appearance order."""
    seen = set(base_order)
    extras = []
    for a in assignments:
        n = a.get("nurse")
        if n and n not in seen:
            seen.add(n)
            extras.append(n)
    return base_order + extras

def first_fit_bias(assignments, nurse_order):
    # Ensure order covers all nurses in data
    order = extend_order_with_unknowns(assignments, nurse_order)

    # Map nurse -> rank (1 = earliest)
    rank = {n: i + 1 for i, n in enumerate(order)}

    # Counts
    counts = Counter(a["nurse"] for a in assignments if "nurse" in a)
    total = sum(counts.values())

    if total == 0:
        return {
            "order": order,
            "counts": counts,
            "total": 0,
            "avg_rank": 0.0,
            "expected_rank": (len(order) + 1) / 2 if order else 0.0,
            "bias_score": 0.0,
            "first_share": 0.0,
        }

    # Average rank used (weighted by assignment count)
    used_ranks_sum = sum(rank[n] * c for n, c in counts.items() if n in rank)
    rbar = used_ranks_sum / total

    # Bias score
    N = len(order)
    expected = (N + 1) / 2 if N > 0 else 0.0
    denom = (N - 1) / 2 if N > 1 else 1.0
    score = (expected - rbar) / denom

    # Share to first nurse
    first_nurse = order[0] if order else None
    first_share = (counts[first_nurse] / total) if first_nurse in counts and total > 0 else 0.0

    return {
        "order": order,
        "counts": counts,
        "total": total,
        "avg_rank": rbar,
        "expected_rank": expected,
        "bias_score": score,
        "first_share": first_share,
    }

if __name__ == "__main__":
    # HARD-CODE YOUR NURSE ORDER HERE 
    nurse_order = ["Patrick", "Andrea", "Stefaan", "Sara", "Nguyen"]

    target = "n21nl"

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="Path to assignments JSON")
    args = ap.parse_args()
    filename = args.json

    parts = filename.split("_")
    print(filename)
    if len(parts) >= 3:  # has at least 3 parts to have a "middle"
        middle = parts[-2]
        if middle == target:
            nurse_order = ["HN_0", "HN_1", "HN_2", "NU_3", "NU_4", "NU_5", "NU_6", "NU_7","NU_8", "NU_9", "NU_10", "CT_11", "CT_12", "CT_13", "CT_14", "CT_15","TR_16", "TR_17", "TR_18", "TR_19", "TR_20"]

    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assignments = data.get("assignments", [])

    result = first_fit_bias(assignments, nurse_order)

    print("Order:", ", ".join(result["order"]))
    print("\nCounts per nurse:")
    for n in result["order"]:
        print(f"  {n}: {result['counts'].get(n, 0)}")
    print(f"\nTotal assignments: {result['total']}")
    print(f"Average rank used: {result['avg_rank']:.3f}  |  Expected: {result['expected_rank']:.3f}")
    print(f"First-fit bias score: {result['bias_score']:.3f}  (1=max bias, 0=no bias, <0=tail bias)")
    if result["order"]:
        print(f"Share to first nurse ({result['order'][0]}): {result['first_share']:.3f}")
