import subprocess
from validator import *


VALIDATOR = "INRC2_validator.jar"
instance = "n005w4_0_1-2-3-3"

# take proposed schedule

# evaluate schedule
try:
    out = subprocess.run(construct_command(instance, VALIDATOR).split(), capture_output=True, text=True, check=True)
    print(out)

except subprocess.CalledProcessError as e:
    print(f"error running validator: {e}")


# if evaluated schedule is good/bad, do action