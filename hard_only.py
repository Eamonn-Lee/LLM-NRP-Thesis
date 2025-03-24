from ortools.sat.python import cp_model
import json

def main():
    # Days of the week
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    full_day_names = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun"
    }
    
    # Nurse data (from the scenario)
    nurses = {
        "Patrick": {"contract": "FullTime", "skills": ["HeadNurse", "Nurse"]},
        "Andrea": {"contract": "FullTime", "skills": ["HeadNurse", "Nurse"]},
        "Stefaan": {"contract": "PartTime", "skills": ["HeadNurse", "Nurse"]},
        "Sara": {"contract": "PartTime", "skills": ["Nurse"]},
        "Nguyen": {"contract": "FullTime", "skills": ["Nurse"]}
    }
    
    # Previous week assignment history (used for forbidden transition on day 0)
    nurse_history = {
        "Patrick": {"lastAssignedShiftType": "Night", "numberOfAssignments": 0,
                    "numberOfWorkingWeekends": 0, "numberOfConsecutiveAssignments": 1,
                    "numberOfConsecutiveWorkingDays": 4, "numberOfConsecutiveDaysOff": 0},
        "Andrea": {"lastAssignedShiftType": "Early", "numberOfAssignments": 0,
                   "numberOfWorkingWeekends": 0, "numberOfConsecutiveAssignments": 3,
                   "numberOfConsecutiveWorkingDays": 3, "numberOfConsecutiveDaysOff": 0},
        "Stefaan": {"lastAssignedShiftType": "None", "numberOfAssignments": 0,
                    "numberOfWorkingWeekends": 0, "numberOfConsecutiveAssignments": 0,
                    "numberOfConsecutiveWorkingDays": 0, "numberOfConsecutiveDaysOff": 3},
        "Sara": {"lastAssignedShiftType": "Late", "numberOfAssignments": 0,
                 "numberOfWorkingWeekends": 0, "numberOfConsecutiveAssignments": 1,
                 "numberOfConsecutiveWorkingDays": 4, "numberOfConsecutiveDaysOff": 0},
        "Nguyen": {"lastAssignedShiftType": "None", "numberOfAssignments": 0,
                   "numberOfWorkingWeekends": 0, "numberOfConsecutiveAssignments": 0,
                   "numberOfConsecutiveWorkingDays": 0, "numberOfConsecutiveDaysOff": 1}
    }
    
    # Shift types and their forbidden succeeding shift types.
    shift_types = ["Early", "Late", "Night"]
    forbidden_transitions = {
        "Early": [],
        "Late": ["Early"],
        "Night": ["Early", "Late"]
    }
    
    # Current week requirements (minimum coverage per day)
    # For each requirement, we convert the keys to the three-letter day abbreviations.
    requirements = [
        {"shiftType": "Early", "skill": "HeadNurse", 
         "requirements": {"Mon": 0, "Tue": 0, "Wed": 1, "Thu": 0, "Fri": 1, "Sat": 0, "Sun": 0}},
        {"shiftType": "Early", "skill": "Nurse", 
         "requirements": {"Mon": 1, "Tue": 1, "Wed": 0, "Thu": 1, "Fri": 0, "Sat": 1, "Sun": 1}},
        {"shiftType": "Late", "skill": "HeadNurse", 
         "requirements": {"Mon": 1, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 1, "Sun": 1}},
        {"shiftType": "Late", "skill": "Nurse", 
         "requirements": {"Mon": 0, "Tue": 1, "Wed": 1, "Thu": 1, "Fri": 1, "Sat": 1, "Sun": 1}},
        {"shiftType": "Night", "skill": "HeadNurse", 
         "requirements": {"Mon": 1, "Tue": 0, "Wed": 1, "Thu": 1, "Fri": 0, "Sat": 0, "Sun": 0}},
        {"shiftType": "Night", "skill": "Nurse", 
         "requirements": {"Mon": 1, "Tue": 1, "Wed": 0, "Thu": 1, "Fri": 0, "Sat": 1, "Sun": 1}}
    ]
    
    # Shift off requests
    shift_off_requests = [
        {"nurse": "Andrea", "shiftType": "Any", "day": "Tuesday"},
        {"nurse": "Stefaan", "shiftType": "Any", "day": "Wednesday"},
        {"nurse": "Nguyen", "shiftType": "Any", "day": "Friday"},
        {"nurse": "Nguyen", "shiftType": "Any", "day": "Saturday"},
        {"nurse": "Sara", "shiftType": "Late", "day": "Saturday"}
    ]
    
    # Create the CP-SAT model
    model = cp_model.CpModel()
    
    # Decision variables: assignment[(nurse, day, shift, skill)] = 1 if nurse is assigned that shift on that day with that skill.
    assignment = {}
    for nurse in nurses:
        for d in range(len(days)):
            for s in shift_types:
                for skill in nurses[nurse]["skills"]:
                    assignment[(nurse, d, s, skill)] = model.NewBoolVar(
                        f'assign_{nurse}_{days[d]}_{s}_{skill}'
                    )
    
    # Constraint 1: Each nurse can work at most one shift per day.
    for nurse in nurses:
        for d in range(len(days)):
            model.Add(sum(assignment[(nurse, d, s, skill)]
                          for s in shift_types for skill in nurses[nurse]["skills"]) <= 1)
    
    # Constraint: Respect shift off requests.
    for request in shift_off_requests:
        nurse = request["nurse"]
        # Map the full day name to our three-letter abbreviation and get its index.
        day_abbr = full_day_names[request["day"]]
        d = days.index(day_abbr)
        if request["shiftType"] == "Any":
            # Nurse must not work any shift on that day.
            model.Add(sum(assignment[(nurse, d, s, skill)]
                          for s in shift_types for skill in nurses[nurse]["skills"]) == 0)
        else:
            # If a specific shift type is requested off, then no assignment for that shift is allowed.
            s_off = request["shiftType"]
            for skill in nurses[nurse]["skills"]:
                model.Add(assignment[(nurse, d, s_off, skill)] == 0)
    
    # Constraint: Forbidden shift transitions.
    # For day 0, use previous week’s lastAssignedShiftType.
    for nurse in nurses:
        last_shift = nurse_history[nurse]["lastAssignedShiftType"]
        if last_shift != "None":
            forbidden = forbidden_transitions.get(last_shift, [])
            for s in forbidden:
                for skill in nurses[nurse]["skills"]:
                    model.Add(assignment[(nurse, 0, s, skill)] == 0)
    
    # For days 1 to 6, enforce that if a nurse worked a shift that forbids a succeeding type,
    # then on the following day that forbidden shift cannot be assigned.
    for nurse in nurses:
        for d in range(1, len(days)):
            for s_prev in shift_types:
                for skill_prev in nurses[nurse]["skills"]:
                    # Determine the forbidden shifts after s_prev.
                    for s_forbid in forbidden_transitions.get(s_prev, []):
                        for skill in nurses[nurse]["skills"]:
                            # If nurse was assigned s_prev on day d-1 then they cannot be assigned s_forbid on day d.
                            model.Add(assignment[(nurse, d, s_forbid, skill)] == 0).OnlyEnforceIf(
                                assignment[(nurse, d-1, s_prev, skill_prev)]
                            )
    
    # Constraint: Cover minimum requirements for each shift type and skill per day.
    for req in requirements:
        shift = req["shiftType"]
        req_skill = req["skill"]
        for day_abbr in days:
            d = days.index(day_abbr)
            min_req = req["requirements"][day_abbr]
            # Sum over all nurses who are qualified (i.e. have the required skill).
            covering = []
            for nurse in nurses:
                if req_skill in nurses[nurse]["skills"]:
                    # Only add the variable if it exists (nurse qualifies for that skill in the given shift).
                    key = (nurse, d, shift, req_skill)
                    if key in assignment:
                        covering.append(assignment[key])
            model.Add(sum(covering) >= min_req)
    
    # Create the solver and solve the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution_assignments = []
        for nurse in nurses:
            for d in range(len(days)):
                for s in shift_types:
                    for skill in nurses[nurse]["skills"]:
                        if solver.Value(assignment[(nurse, d, s, skill)]) == 1:
                            solution_assignments.append({
                                "nurse": nurse,
                                "day": days[d],
                                "shiftType": s,
                                "skill": skill
                            })
        output = {"assignments": solution_assignments}
        with open("solution.json", "w") as f:
            json.dump(output, f, indent=4)
        print("Solution written to solution.json")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
