import json
from collections import defaultdict
import pprint

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def update_history_with_solution(history, solution):
    # Build a lookup from nurse name → existing history
    previous = {entry["nurse"]: entry for entry in history["nurseHistory"]}
    #pprint.pp(previous)

    # Prepare current week shifts: nurse → ["None", ..., "Early", ..., "None"]
    current_week = defaultdict(lambda: ["None"] * 7)
    for assignment in solution["assignments"]:
        nurse = assignment["nurse"]
        idx = DAYS.index(assignment["day"])
        shift = assignment["shiftType"]
        current_week[nurse][idx] = shift

    updated_nurse_history = []

    for nurse, shifts in current_week.items():
        prev = previous.get(nurse, {
            "numberOfAssignments": 0,
            "numberOfWorkingWeekends": 0,
            "lastAssignedShiftType": "None",
            "numberOfConsecutiveAssignments": 0,
            "numberOfConsecutiveWorkingDays": 0,
            "numberOfConsecutiveDaysOff": 0
        })

        # Total assignments
        weekly_assignments = sum(1 for s in shifts if s != "None")
        new_total_assignments = prev["numberOfAssignments"] + weekly_assignments

        # Weekend work
        worked_weekend = any(shifts[DAYS.index(d)] != "None" for d in ["Sat", "Sun"])
        new_total_working_weekends = prev["numberOfWorkingWeekends"] + (1 if worked_weekend else 0)

        # Last shift worked this week
        last_shift_this_week = shifts[-1]

        # Update consecutive assignments
        if last_shift_this_week != "None":
            # Count how many times last shift type appears from end
            consecutive = 0
            for s in reversed(shifts):
                if s == last_shift_this_week:
                    consecutive += 1
                elif s != "None":
                    break
                else:
                    break
            if prev["lastAssignedShiftType"] == last_shift_this_week:
                consecutive += prev["numberOfConsecutiveAssignments"]
        else:
            consecutive = 0

        # Consecutive working days
        full_week = True
        consec_working_days = 0
        for s in reversed(shifts):
            if s != "None":
                consec_working_days += 1
            else:
                full_week = False
                break

        # If the streak reaches to the end of the week, extend it with the previous week's streak
        if shifts[-1] != "None" and full_week:  #needs to have had shift everyday of week
            consec_working_days += prev["numberOfConsecutiveWorkingDays"]



        # Consecutive days off
        off_streak = 0
        for s in reversed(shifts):
            if s == "None":
                off_streak += 1
            else:
                break

        if all(s == "None" for s in shifts):
            off_streak += prev["numberOfConsecutiveDaysOff"]

        updated_nurse_history.append({
            "nurse": nurse,
            "numberOfAssignments": new_total_assignments,
            "numberOfWorkingWeekends": new_total_working_weekends,
            "lastAssignedShiftType": last_shift_this_week,
            "numberOfConsecutiveAssignments": consecutive,
            "numberOfConsecutiveWorkingDays": consec_working_days ,
            "numberOfConsecutiveDaysOff": off_streak
        })

    # Include nurses who had no assignments this week (keep their streaks updated)
    for nurse in previous:
        if nurse not in current_week:
            prev = previous[nurse]
            updated_nurse_history.append({
                "nurse": nurse,
                "numberOfAssignments": prev["numberOfAssignments"],
                "numberOfWorkingWeekends": prev["numberOfWorkingWeekends"],
                "lastAssignedShiftType": "None",
                "numberOfConsecutiveAssignments": 0,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveDaysOff": prev["numberOfConsecutiveDaysOff"] + 7
            })

    return {
        "week": solution["week"] + 1,
        "scenario": solution["scenario"],
        "nurseHistory": updated_nurse_history   #sorted(updated_nurse_history, key=lambda x: x["nurse"])
    }


def update(his_fp, update_week_fp):
    TESTDIRR = "11_6_3"

    with open(his_fp) as f:
        history = json.load(f)

    with open(update_week_fp) as f:   #CHANGE
        solution = json.load(f)

    new_history = update_history_with_solution(history, solution)

    with open(his_fp, "w") as f:
        json.dump(new_history, f, indent=2)
