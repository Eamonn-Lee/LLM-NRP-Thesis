import json
import sys
import pprint

def open_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def update_history(history, sol):
    """
    Shove in most recent week into history file
    """
    history['week'] += 1
    for ass in sol["assignments"]:
        print(ass)
        for nurse_dict in history["nurseHistory"]:
            if nurse_dict.get("nurse") == ass["nurse"]:
                #UPDATE EVERYTHING
                nurse_dict["numberOfAssignments"] += 1
                #nurse_dict["numberOfWorkingWeekends"]
                nurse_dict["lastAssignedShiftType"] = ass["shiftType"]
                #nurse_dict["numberOfConsecutiveAssignments"]   #consecutive shift types
                #nurse_dict["numberOfConsecutiveWorkingDays"]   #consecutive working days
                #nurse_dict["numberOfConsecutiveDaysOff"]       #consecutive days off

                 


    pprint.pp(history)
    return 0



if __name__ == "__main__":
    hist_path = "json_Dataset/n005w4/H0-n005w4-0.json"
    sol_path = "27_2/1-0.json"

    his = open_json(hist_path)
    week = open_json(sol_path)

    if his and week:
        update_history(his, week)
    else:
        raise("Almost certainly failure to load")
