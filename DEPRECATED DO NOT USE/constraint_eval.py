import json
from collections import defaultdict
from util import *
import pprint

#Completed -> requires testing
#mischek says 285 for week1

JSONPATH = "json_Dataset/"
DATASET = "n005w4"

fp = JSONPATH+DATASET

SCE=    "/Sc-"+DATASET+".json"
WK=     "/WD-"+DATASET+"-1"+".json"    #CHANGE FOR WEEK
HIS=    "/H0-"+DATASET+"-0"+".json"  #CHANGE for HIS

#SOL=    fp+ "/Solution_H_0-WD_1-2-3-3/Sol-n005w4-1-0.json"     #CHANGE TO RESULTS
SOL=    "gpt_r.json"     #CHANGE TO RESULTS

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYSLONG = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

PENALTIES = {
    "S1_optimal_staffing": 30,
    "S2_consecutive_shift": 15,     #shift
    "S2_consecutive_working": 30,   #day
    "S3_consecutive_off": 30,
    "S4_preferences": 10,
    "S5_complete_weekend": 30
}

scenario = load_scenario(fp+SCE)
week_data = load_week_data(fp+WK)
history = load_history(fp+HIS)
assignments = load_solution(SOL)


# Helper to convert requirement list into daily dictionary
def get_requirements_by_day():
    reqs = defaultdict(lambda: defaultdict(lambda: {"min": 0, "opt": 0}))
    for r in week_data["requirements"]:
        for i, day in enumerate(DAYSLONG):
            min_req = r[f"requirementOn{day}"]["minimum"]
            opt_req = r[f"requirementOn{day}"]["optimal"]
            reqs[day][(r["shiftType"], r["skill"])] = {"min": min_req, "opt": opt_req}
    return reqs

def calc_S1():  #optimal coverage
    reqs = get_requirements_by_day()
    coverage = defaultdict(lambda: defaultdict(int))

    for nurse, sched in assignments.items():
        #id, [day: shifttype]
        for day, shift in sched.items():
            skill = get_assignment_skill(nurse, day)
            coverage[day][(shift, skill)] += 1  #CORRECT

    penalty = 0
    for day in DAYSLONG:
        for (shift, skill), req in reqs[day].items():
            #print(f"{shift}+{skill} = {req}")   #just WD data

            actual = coverage[day[:3]][(shift, skill)]  #dirty truncate translate
            missing = max(0, req["opt"] - actual)
            penalty += missing * PENALTIES["S1_optimal_staffing"]
    return penalty


def calc_S2():  #consecutive assignments
    shift_dict = {s["id"]: s for s in scenario["shiftTypes"]}
    penalty = 0
    for nurse, sched in assignments.items():
        cdp = 0
        csp = 0

        nurse_contract = next((d for d in scenario["nurses"] if d["id"] == nurse))["contract"]  #String(contract type)

        contract = next((d for d in scenario["contracts"] if d["id"] == nurse_contract))    #contract dict

        work_flags = [1 if day in sched else 0 for day in DAYS]

        # Consecutive working days
        streak = history[nurse]["consec_work"]
        #print(work_flags)   # list of boolean "worked day", len 7
        for work in work_flags:
            if work:
                streak += 1
                if streak > contract["maximumNumberOfConsecutiveWorkingDays"]:
                    cdp += PENALTIES["S2_consecutive_working"]  #each day worked over contract 
            else:   #did not work
                if 0 < streak < contract["minimumNumberOfConsecutiveWorkingDays"]:
                    cdp += (contract["minimumNumberOfConsecutiveWorkingDays"] - streak)*PENALTIES["S2_consecutive_working"]
                streak = 0

        #-----------------------------
        #SHIFT type
        #for each nurse

        #print("----")
        curr_shift = history[nurse]["last"]
        curr_streak = history[nurse]["consec_shift"]

        for day in DAYS:
            shift = sched.get(day)  #look at current shift of a nurse

            if shift != None and shift == curr_shift:
                curr_streak +=1
                #print(f"{day}-S")

                if curr_streak > shift_dict[shift]["maximumNumberOfConsecutiveAssignments"]:
                    #print(shift)
                    csp += PENALTIES["S2_consecutive_shift"]

            else:   #no longer in shift streak
                #print(f"{day}-B")
                #Only calculate under shift if we transition from (current shift == actual shift) to something else
                if curr_shift != None and 0 < curr_streak < shift_dict[curr_shift]["minimumNumberOfConsecutiveAssignments"]:
                    #print(f"{curr_shift}->{shift}")
                    x = shift_dict[curr_shift]["minimumNumberOfConsecutiveAssignments"]
                    #print(f"{x} - {curr_streak}")
                
                    csp += (shift_dict[curr_shift]["minimumNumberOfConsecutiveAssignments"] - curr_streak)* PENALTIES["S2_consecutive_shift"]
                #reset streak types
                curr_shift = shift
                curr_streak = 1



#           Per shift-type
#        for shift_type in scenario["shiftTypes"]:
#            print(history[nurse])
#            streak = history[nurse]["consec_shift"] if history[nurse]["last"] == shift_type["id"] else 0
#            #print(streak)
#            #print(shift_type["id"])
#            for day in DAYS:
#                shift = sched.get(day)  #gives shift worked on day
#                
#                if shift == shift_type["id"]:
#                    streak += 1 #additional day in range worked
#
#                    if streak > shift_type["maximumNumberOfConsecutiveAssignments"]:
#                        csp += PENALTIES["S2_consecutive_shift"]
#
#                else:
#                    if 0 < streak < shift_type["minimumNumberOfConsecutiveAssignments"]:
#                        csp += (shift_type["minimumNumberOfConsecutiveAssignments"]-streak)*PENALTIES["S2_consecutive_shift"]
#                    streak = 0


        penalty += (cdp+csp)

        #print(f"{cdp} : {csp}")
        
    return penalty


def calc_S3():  #consecutive days off
    penalty = 0
    for nurse in scenario["nurses"]:

        nurse_contract = next((d for d in scenario["nurses"] if d["id"] == nurse["id"]))["contract"]  #String(contract type)

        contract = next((d for d in scenario["contracts"] if d["id"] == nurse_contract))    #contract dict

        #contract = scenario["contracts"][scenario["nurses"][nurse]["contract"]]
        sched = assignments.get(nurse["id"], {})

        off_flags = [1 if day not in sched else 0 for day in DAYS]
        #print(off_flags)
        streak = history[nurse["id"]]["consec_off"]
        #print(streak)
        for off in off_flags:
            if off:
                streak += 1
                if streak > contract["maximumNumberOfConsecutiveDaysOff"]:
                    penalty += PENALTIES["S3_consecutive_off"]
            else:
                if 0 < streak < contract["minimumNumberOfConsecutiveDaysOff"]:
                    penalty += PENALTIES["S3_consecutive_off"]
                streak = 0
    return penalty


def calc_S4():  #preferencing       
    prefs = week_data["shiftOffRequests"]
    #print(prefs)
    penalty = 0
    for req in prefs:
        nurse, day, shift = req["nurse"], req["day"], req["shiftType"]
        #print(nurse, day, shift)
        
        assigned_shift = assignments.get(nurse, {}).get(day[:3])

        #print(assignments.get(nurse, {}))

        #print(assigned_shift)
        if assigned_shift:
            if shift == "Any" or shift == assigned_shift:
                #print(nurse, day, shift)   #info of broken preference

                penalty += PENALTIES["S4_preferences"]
    return penalty


def calc_S5():  #weekends
    penalty = 0
    for nurse in scenario["nurses"]:

        nurse_contract = next((d for d in scenario["nurses"] if d["id"] == nurse["id"]))["contract"]  #String(contract type)
        contract = next((d for d in scenario["contracts"] if d["id"] == nurse_contract))    #contract dict

        if contract["completeWeekends"]:
            sched = assignments.get(nurse["id"], {})
            sat = sched.get("Sat")
            sun = sched.get("Sun")
            if (sat is None) != (sun is None):
                penalty += PENALTIES["S5_complete_weekend"]
    return penalty

def get_assignment_skill(nurse, day):
    # Determine skill from actual assignment
    for entry in json.load(open(SOL))["assignments"]:
        if entry["nurse"] == nurse and entry["day"] == day:
            return entry["skill"]
    print("ERROR: SKILL?")
    return "Nurse"  # Fallback if not found

def calc_H1():  #single asas
    daily_assignments = {day: defaultdict(list) for day in DAYS}
    violations = []
    print(assignments)

    for nurse, sched in assignments.items():
        for day, shift in sched.items():
            if day in DAYS:
                daily_assignments[day][nurse].append(shift)
                print(daily_assignments[day][nurse])
            else:
                print(f"WARNING: Unknown day '{day}' for nurse {nurse}")

    pprint.pp(daily_assignments)

    for day, nurses in daily_assignments.items():
        for nurse, shifts in nurses.items():
            if len(shifts) > 1:
                violations.append({
                    "day": day,
                    "nurse": nurse,
                    "shifts": shifts
                })

    return violations

def calc_H2():  #understaff
    # Get min staffing requirements from week data
    reqs = get_requirements_by_day()
    
    # Track actual coverage: day -> (shift, skill) -> count
    coverage = defaultdict(lambda: defaultdict(int))

    for nurse, sched in assignments.items():
        for day_short, shift in sched.items():
            # Defensive: convert day_short to DAYSLONG to match reqs keys
            day_index = DAYS.index(day_short) if day_short in DAYS else None
            if day_index is None:
                print(f"WARNING: Unknown day '{day_short}' for nurse {nurse}")
                continue
            day_long = DAYSLONG[day_index]

            skill = get_assignment_skill(nurse, day_short)
            coverage[day_long][(shift, skill)] += 1

    # Now check for any understaffed (actual < required min)
    violations = []
    for day in DAYSLONG:
        for (shift, skill), req in reqs[day].items():
            actual = coverage[day].get((shift, skill), 0)
            if actual < req["min"]:
                violations.append({
                    "day": day,
                    "shift": shift,
                    "skill": skill,
                    "required_min": req["min"],
                    "actual": actual
                })

    return violations

def calc_H3():  #shift succ
    # Build forbidden pairs
    forbidden_pairs = set()
    for entry in scenario["forbiddenShiftTypeSuccessions"]:
        preceding = entry["precedingShiftType"]
        for succeeding in entry["succeedingShiftTypes"]:
            forbidden_pairs.add((preceding, succeeding))

    violations = []

    for nurse, sched in assignments.items():
        week_shifts = [sched.get(day) for day in DAYS]

        prev_shift = history[nurse]["last"]
        prev_day = "HISTORICAL"

        for i, curr_shift in enumerate(week_shifts):
            curr_day = DAYS[i]

            if prev_shift is not None and curr_shift is not None:
                if (prev_shift, curr_shift) in forbidden_pairs:
                    violations.append({
                        "nurse": nurse,
                        "from_day": prev_day,
                        "from_shift": prev_shift,
                        "to_day": curr_day,
                        "to_shift": curr_shift
                    })

            if curr_shift is not None:
                prev_shift = curr_shift
                prev_day = curr_day
            else:
                prev_shift = None
                prev_day = None

    return violations

def calc_H4():
    return None

def compute_hard():
    return {
        "H1": calc_H1(),
        #"H2": calc_H2(),
        #H3": calc_H3(),
        "H4": calc_H4()
    }

def compute_all_weekly_penalties():
    return {
        "S1": calc_S1(),
        "S2": calc_S2(),
        "S3": calc_S3(),
        "S4": calc_S4(),
        "S5": calc_S5()
    }

if __name__ == "__main__":
    hard = compute_hard()
    for k, v in hard.items():
        pprint.pp(f"{k} : {v}")

    results = compute_all_weekly_penalties()
    total = sum(results.values())
    for k, v in results.items():
        print(f"{k} penalty: {v}")
    print(f"Total weekly penalty: {total}")

"""
S1 penalty: 0
S2 penalty: 30 -> 90?
S3 penalty: 90
S4 penalty: 0
S5 penalty: 0
Total weekly penalty: 120
"""