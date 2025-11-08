import os
from dotenv import load_dotenv
from mistralai import Mistral
from string import Template
import re
import sys

# === === === CONFIG === === ===

DEFAULT_INSTANCE = "n005w4_0_1-2-3-3"
INSTANCE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INSTANCE
MISTRAL_MODEL = "mistral-large-latest"

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
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY not found.")

# === === === INIT CLIENT === === ===

mistral_client = Mistral(api_key=MISTRAL_API_KEY)

print("\n✅ Mistral API key loaded.")
print(f"✅ Prompt length: {len(filled_prompt)} chars")

# === === === MAIN LOOP === === ===

iteration = 1
full_output = ""

messages = [
    {"role": "system", "content": constraint},
    {"role": "user", "content": filled_prompt}
]

while True:
    print(f"\n=== Mistral Call #{iteration} ===")

    response = mistral_client.chat.complete(
        model=MISTRAL_MODEL,
        messages=messages
    )

    output = response.choices[0].message.content
    print("\n=== PARTIAL OUTPUT ===\n")
    print(output)

    # Save chunk
    part_file = f"output_mistral_part_{iteration}.txt"
    with open(part_file, "w") as f:
        f.write(output)
    print(f"\n✅ Saved partial output to {part_file}")

    full_output += output + "\n"

    if re.search(r"CONTINUATION\b", output, re.IGNORECASE):
        print("\n🔄 CONTINUATION detected → resuming...")
        continuation_prompt = (
            "CONTINUE from where you left off. "
            "Resume exactly at the next unassigned shift-day-skill. "
            "Keep the same step-by-step reasoning and running penalty total. "
            "Do not repeat any shifts already assigned."
        )
        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": continuation_prompt})
        iteration += 1
    else:
        print("\n✅ No CONTINUATION found. Mistral run complete!")
        break

# Save final output
final_file = "output_mistral_combined.txt"
with open(final_file, "w") as f:
    f.write(full_output)
print(f"\n✅ Saved final combined output to {final_file}")
