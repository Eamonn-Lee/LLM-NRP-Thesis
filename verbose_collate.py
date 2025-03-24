import re
import pprint
import pandas as pd

def normalize_whitespace(text):
    return "".join(text.split())  # Remove all whitespace characters

def check_string_in_file(file_path, search_string):
    template = {
        "Maximumtotalnumberofassignments": 0,
        "Minimumnumberofconsecutiveshifttypes": 0,
        "Maximumnumberofconsecutiveshifttypes":0,    #no need to diff, interpreted by same rule
        "Minimumnumberofconsecutiveworkingdays":0,
        "Maximumnumberofconsecutiveworkingdays":0,
        "Minimumnumberofconsecutivedaysoff":0,
        "Maximumnumberofworkingweekendsexceeded":0,
        "Completeworkingweekends":0  
    }

    data = [template.copy() for _ in range(28)] #ERROR IF LARGER THAN 4 WEEKS

    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            for penalty in search_string:
                if penalty in normalize_whitespace(line):
                    #print(f"Match: {line.strip()} - {penalty}")
                    day = grab_day(line)
                    data[day][penalty] +=1

    return data



def grab_day(text):
    match = re.search(r'day:\s*(\d+)', text)
    return int(match.group(1)) if match else None

file_path = "verbose.txt" 

raw_search_strings = [
    "Maximum total number of assignments",
    "Minimum number of consecutive shift types",
    "Maximum number of consecutive shift types",    #no need to diff, interpreted by same rule
    "Minimum number of consecutive working days",
    "Maximum number of consecutive working days",
    "Minimum number of consecutive days off",
    "Maximum number of working weekends exceeded",
    "Complete working weekends"                    #noncomplete?
]

search = [normalize_whitespace(x) for x in raw_search_strings]

s = check_string_in_file(file_path, search)

df = pd.DataFrame(s)

pd.set_option('display.max_rows', None)  # Set to None to display all rows
pd.set_option('display.max_columns', None)  # Set to None to display all columns

print(df)
df.to_csv("output.csv", index=False)
