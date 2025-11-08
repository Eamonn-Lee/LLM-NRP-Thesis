import os
from dotenv import load_dotenv
from openai import OpenAI
from string import Template
import re
import sys

# === === === CONFIG === === ===

DEFAULT_INSTANCE = "n005w4_0_1-2-3-3"
INSTANCE = sys.argv[1] if len(sys.argv) > 1 else "DEFAULT_INSTANCE"
MODEL = "gpt-4o"  # or any model you prefer


# === === === LOAD PROMPTS === === ===

with open("prompt_nl.txt", "r") as f:
    template = f.read()

#with open("constraints_nl.txt", "r") as f:
with open("constraints_mm.txt", "r") as f:
    constraint = f.read()

from util import init
files = init(INSTANCE)

with open(files["his"], "r") as f:
    his = f.read()

with open(files["sce"], "r") as f:
    sce = f.read()

with open(files["week"][0], "r") as f:
    wk0 = f.read()

prompt = Template(template)
filled_prompt = prompt.substitute(
    scenario=sce,
    history=his,
    week=wk0
)

# === === === LOAD API KEY === === ===

load_dotenv("config.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment.")

client = OpenAI(api_key=OPENAI_API_KEY)

# === === === INIT CONVERSATION === === ===

messages = [
    {
        "role": "system",
        "content": constraint
    },
    {
        "role": "user",
        "content": filled_prompt
    }
]

# === === === MAIN LOOP === === ===

iteration = 1
full_output = ""

print(f"\n✅ Loaded OpenAI API key: {bool(OPENAI_API_KEY)}")
print(f"✅ Using model: {MODEL}")

while True:
    print(f"\n=== LLM Call #{iteration} ===")

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3
    )

    output = response.choices[0].message.content
    print("\n=== PARTIAL OUTPUT ===\n")
    print(output)

    # Save chunk to file
    part_file = f"output_part_{iteration}.txt"
    with open(part_file, "w") as f:
        f.write(output)
    print(f"\n✅ Saved partial output to {part_file}")

    full_output += output + "\n"

    # Check for CONTINUATION marker (case-insensitive, trailing whitespace OK)
    if re.search(r"CONTINUATION\b", output, re.IGNORECASE):
        print("\n🔄 CONTINUATION detected → resuming...")

        # Add assistant's answer
        messages.append({
            "role": "assistant",
            "content": output
        })

        # Add follow-up user prompt to continue
        messages.append({
            "role": "user",
            "content": "CONTINUE from where you left off. Resume exactly at the next unassigned shift-day-skill. Keep the same step-by-step reasoning and running penalty total. Do not repeat any shifts already assigned."
        })

        iteration += 1

    else:
        print("\nNo CONTINUATION found. Roster is complete!")
        break

# === === === SAVE FINAL OUTPUT === === ===

with open("output_gpt.txt", "w") as f:
    f.write(full_output)

print("\nSaved full combined output to output_combined.txt")