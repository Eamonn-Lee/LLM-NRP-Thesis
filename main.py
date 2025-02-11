import subprocess
from validator import *


VALIDATOR = "INRC2_validator.jar"
instance = "n005w4_0_1-2-3-3"

# take proposed schedule

# evaluate schedule
try:
    res = subprocess.check_output(construct_command(instance, VALIDATOR).split(), text=True)
    print(res)

except subprocess.CalledProcessError as e:
    print(f"error running validator: {e}")

total_cost = subprocess.check_output(["grep", "Total cost: "], input=res, text=True)
print(total_cost)
# if evaluated schedule is good/bad, do action

if bad_outcome(total_cost):
    exit()