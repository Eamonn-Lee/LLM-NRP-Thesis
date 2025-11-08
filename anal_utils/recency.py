import argparse
import json
from collections import defaultdict
import math  # NEW: for sqrt

DAY_ORDER = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
DEFAULT_SHIFT_ORDER = ["Early","Day","Late","Night"]

def build_sequence(assignments, use_day_order=False, shift_order=None):
    if not use_day_order:
        # Keep given order
        seq = list(enumerate(assignments))  # (idx, assignment)
        return [a for idx, a in seq]

    # Sort by day, then by shift
    shift_rank = {s:i for i,s in enumerate(shift_order or DEFAULT_SHIFT_ORDER)}
    day_rank = {d:i for i,d in enumerate(DAY_ORDER)}

    def key(a):
        d = a.get("day")
        s = a.get("shiftType")
        return (day_rank.get(d, 99), shift_rank.get(s, 99))

    return sorted(assignments, key=key)

def average_gap(indices):
    if len(indices) < 2:
        return None  # Not enough data to compute a gap
    diffs = [b - a for a, b in zip(indices, indices[1:])]
    return sum(diffs) / len(diffs)

# NEW: coefficient of variation (population)
def coefficient_of_variation(values):
    """
    Population CV = std / mean. Ignores None values.
    Returns None if not enough data or mean==0.
    """
    xs = [x for x in values if x is not None]
    if len(xs) == 0:
        return None
    mean = sum(xs) / len(xs)
    if mean == 0:
        return None
    var = sum((x - mean) ** 2 for x in xs) / len(xs)  # population variance
    sd = math.sqrt(var)
    return sd / mean

def compute_recency_bias(assignments, use_day_order=False, shift_order=None):
    seq = build_sequence(assignments, use_day_order=use_day_order, shift_order=shift_order)

    # Map nurse -> list of sequence positions
    pos = defaultdict(list)
    for i, a in enumerate(seq):
        n = a.get("nurse")
        if n is not None:
            pos[n].append(i)

    # Compute average gap per nurse
    results = []
    for nurse, idxs in pos.items():
        avg = average_gap(idxs)
        results.append({
            "nurse": nurse,
            "count": len(idxs),
            "avg_gap": avg  # None if only 1 assignment
        })

    # Sort by avg_gap ascending (smallest gap = most frequent reuse)
    results.sort(key=lambda r: (float('inf') if r["avg_gap"] is None else r["avg_gap"], r["nurse"]))
    return results, len(seq)

def print_report(results, total_len, sequence_label):
    print(f"=== Recency Bias ({sequence_label}) ===")
    print(f"Total assignments in sequence: {total_len}\n")
    print("nurse, count, avg_gap (smaller => more frequent reuse)")
    for r in results:
        avg = "NA" if r["avg_gap"] is None else f"{r['avg_gap']:.2f}"
        print(f"{r['nurse']}, {r['count']}, {avg}")

    # NEW: CV summary
    counts = [r["count"] for r in results]
    gaps = [r["avg_gap"] for r in results if r["avg_gap"] is not None]
    cv_counts = coefficient_of_variation(counts)
    cv_gaps = coefficient_of_variation(gaps)

    print("\nImbalance (Coefficient of Variation)")
    print(f"  counts:  {cv_counts:.3f}" if cv_counts is not None else "  counts:  NA")
    print(f"  avg_gap: {cv_gaps:.3f}" if cv_gaps is not None else "  avg_gap: NA")
    print()

def recency():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="Path to assignments JSON")
    ap.add_argument("--use-day-order", action="store_true", help="Sort sequence by day then shift")
    ap.add_argument("--shift-order", help='Comma-separated shift order for --use-day-order (default "Early,Day,Late,Night")')
    args = ap.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assignments = data.get("assignments", [])
    shift_order = [s.strip() for s in args.shift_order.split(",")] if args.shift_order else None

    # Optional day-order
    results_day, L_day = compute_recency_bias(assignments, use_day_order=True, shift_order=shift_order)
    print_report(results_day, L_day, "day+shift order")

if __name__ == "__main__":
    recency()
