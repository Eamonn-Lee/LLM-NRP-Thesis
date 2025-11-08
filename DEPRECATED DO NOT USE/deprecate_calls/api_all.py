import subprocess

INSTANCE = "n005w4_0_1-2-3-3"
#INSTANCE = "n021w4_2_8-1-4-3"

scripts = [
    "api_claude.py",
    "api_gpt.py",
    "api_gemini.py",
    "api_mistral.py"
]

for script in scripts:
    print(f"Running {script} with INSTANCE={INSTANCE}")
    subprocess.run(["python3", script, INSTANCE])
