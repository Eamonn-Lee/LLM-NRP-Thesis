import json
from collections import defaultdict
import pprint

# === Utility Functions ===

def load_json(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

# === H1: Duplicate shifts per day per nurse ===

def find_duplicate_assignments(assignments):
    nurse_day_assignments = defaultdict(set)
    duplicates = []
    for a in assignments:
        key = (a["nurse"], a["day"])
        if key in nurse_day_assignments:
            duplicates.append(a)
        else:
            nurse_day_assignments[key].add(a["shiftType"])
    return duplicates

# === H2: Understaffing ===

DAY_ABBREVIATION_TO_FULL = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday"
}

def count_assignments(assignments):
    """
    Count how many nurses are assigned for each (full_day, shiftType, skill).
    Returns: counts[day][shiftType][skill] = number of assigned nurses
    """
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for a in assignments:
        short_day = a["day"]
        full_day = DAY_ABBREVIATION_TO_FULL.get(short_day, short_day)  # fallback if full already
        shift = a["shiftType"]
        skill = a["skill"]
        counts[full_day][shift][skill] += 1
    return counts

def check_minimum_requirements(requirements, assignment_counts):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    violations = []
    for req in requirements:
        shift = req["shiftType"]
        skill = req["skill"]
        for day in days:
            required_min = req[f"requirementOn{day}"]["minimum"]
            assigned = assignment_counts[day].get(shift, {}).get(skill, 0)
            if assigned < required_min:
                violations.append({
                    "day": day,
                    "shiftType": shift,
                    "skill": skill,
                    "requiredMinimum": required_min,
                    "assigned": assigned
                })
    return violations

# === H3: Forbidden Successions ===

DAY_ABBREVIATION_TO_FULL = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday"
}

def build_weekly_shift_map(assignments):
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    shift_map = defaultdict(lambda: {day: "None" for day in days_order})
    
    for a in assignments:
        nurse = a["nurse"]
        short_day = a["day"]
        full_day = DAY_ABBREVIATION_TO_FULL.get(short_day, short_day)
        shift = a["shiftType"]
        shift_map[nurse][full_day] = shift

    return {
        nurse: [day_shifts[day] for day in days_order]
        for nurse, day_shifts in shift_map.items()
    }

def extract_forbidden_pairs(scenario_data):
    forbidden_pairs = set()
    for rule in scenario_data["forbiddenShiftTypeSuccessions"]:
        prev = rule["precedingShiftType"]
        for succ in rule["succeedingShiftTypes"]:
            forbidden_pairs.add((prev, succ))
    return forbidden_pairs

def check_forbidden_successions(scenario_data, assignments, nurse_history):
    forbidden_pairs = extract_forbidden_pairs(scenario_data)
    shift_sequences = build_weekly_shift_map(assignments)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Map nurse history
    history_map = {
        h["nurse"]: h.get("lastAssignedShiftType", "None") or "None"
        for h in nurse_history
    }

    violations = []
    for nurse, shift_list in shift_sequences.items():
        # Prepend historic shift
        last_shift = history_map.get(nurse, "None")
        full_shift_sequence = [last_shift] + shift_list

        for i in range(len(shift_list)):  # compare 0→Mon, 1→Tue, ..., 6→Sun
            prev_shift = full_shift_sequence[i]
            next_shift = full_shift_sequence[i + 1]
            if prev_shift == "None":
                continue  # Any shift can follow None
            if (prev_shift, next_shift) in forbidden_pairs:
                violations.append({
                    "nurse": nurse,
                    "day": days[i],
                    "precedingShift": prev_shift,
                    "succeedingShift": next_shift
                })

    return violations


def check_skill_violations(assignments, scenario_data):
    """
    Checks if each nurse assignment is valid based on their listed skills.
    Returns a list of violations where a nurse is assigned outside their skill set.
    """
    # Build map of nurse -> set of skills
    skill_map = {
        nurse["id"]: set(nurse["skills"])
        for nurse in scenario_data["nurses"]
    }

    violations = []
    for a in assignments:
        nurse = a["nurse"]
        skill = a["skill"]
        if skill not in skill_map.get(nurse, set()):
            violations.append({
                "nurse": nurse,
                "day": a["day"],
                "shiftType": a["shiftType"],
                "assignedSkill": skill,
                "nurseSkills": list(skill_map.get(nurse, []))
            })
    return violations

def main():
    schedule_path = "gpt_r.json"

    requirements_path = "json_Dataset/n005w4/WD-n005w4-1.json"
    scenario_path = "json_Dataset/n005w4/Sc-n005w4.json"
    history_path = "json_Dataset/n005w4/H0-n005w4-0.json"

    #requirements_path = "json_Dataset/n021w4/WD-n021w4-8.json"
    #scenario_path = "json_Dataset/n021w4/Sc-n021w4.json"
    #history_path = "json_Dataset/n021w4/H0-n021w4-2.json"

    schedule_data = load_json(schedule_path)
    requirements_data = load_json(requirements_path)
    scenario_data = load_json(scenario_path)
    history_data = load_json(history_path)

    assignments = schedule_data["assignments"]
    requirements = requirements_data["requirements"]
    nurse_history = history_data["nurseHistory"]

    violations_dict = {}

    # H1: Duplicate shifts
    violations_dict["H1"] = find_duplicate_assignments(assignments)

    # H2: Understaffing
    assignment_counts = count_assignments(assignments)
    violations_dict["H2"] = check_minimum_requirements(requirements, assignment_counts)

    # H3: Forbidden successions
    violations_dict["H3"] = check_forbidden_successions(scenario_data, assignments, nurse_history)

    # H4: Skill qualification
    violations_dict["H4"] = check_skill_violations(assignments, scenario_data)

    # No printout
    return violations_dict

if __name__ == "__main__":
    violations = main()
    pprint.pp(violations)

    for i in violations.keys():
        print(len(violations[i]))