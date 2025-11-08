import json
from collections import defaultdict

# Helper functions to load external JSON files
def load_scenario(filename="scenario.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_week_data(filename="week_data.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_history(filename="history.json"):
    data = json.load(open(filename))
    return {n["nurse"]: {
        "last": n["lastAssignedShiftType"],
        "consec_shift": n["numberOfConsecutiveAssignments"],
        "consec_work": n["numberOfConsecutiveWorkingDays"],
        "consec_off": n["numberOfConsecutiveDaysOff"]
    } for n in data["nurseHistory"]}

def load_solution(filename="solution.json"):
    data = json.load(open(filename))
    result = defaultdict(dict)
    for a in data["assignments"]:
        result[a["nurse"]][a["day"]] = a["shiftType"]
    return result

