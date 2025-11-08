import os
import json
from collections import defaultdict

DATASET_DIRR = "json_Dataset"  #link dataset

def assert_file(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"file not found: {filepath}")
    
def init(instance):
    instance = instance.split('_')
    dataset = instance[0]
    his = instance[1]
    order = instance[2].split('-')

    sce_file=f"{DATASET_DIRR}/{dataset}/Sc-{dataset}.json"
    assert_file(sce_file)
    his_file=f"{DATASET_DIRR}/{dataset}/H0-{dataset}-{his}.json"
    assert_file(his_file)

    week_files = [f"{DATASET_DIRR}/{dataset}/WD-{dataset}-{x}.json" for x in order]

    return {
        "sce": sce_file,
        "his": his_file,
        "week": week_files,
    }

# helper functions to load external JSON files
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

