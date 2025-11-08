import os

#Iter roster to full json naming data

# Hardcoded old and new file names
old_names = [
    "cr.json",
    "ge.json",
    "gp.json",
    "mr.json"
]

instance = "n5mm" + "_"
iter = "4"

new_names = [
    "claude_"+instance + iter+".json",
    "gemini_"+instance + iter+".json",
    "gpt_"+instance + iter+".json",
    "mistral_"+instance + iter+".json"
]

for old, new in zip(old_names, new_names):
    if os.path.exists(old):
        os.rename(old, new)
        print(f"Renamed {old} → {new}")
    else:
        print(f"File not found: {old}")