import os
from dotenv import load_dotenv
import google.generativeai as genai
from string import Template
import re
import sys

# === === === CONFIG === === ===

DEFAULT_INSTANCE = "n005w4_0_1-2-3-3"
INSTANCE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INSTANCE
GEMINI_MODEL = "gemini-1.5-flash"

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found.")

genai.configure(api_key=GEMINI_API_KEY)

print("\n✅ Gemini API key loaded.")
print(f"✅ Prompt length: {len(filled_prompt)} chars")

# === === === MAIN LOOP === === ===

iteration = 1
full_output = ""

# The 'constraint' file is used as a system-level instruction for the model.
model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=constraint)

# Start the chat session with an empty history.
# The system instruction is part of the model, and we will send the first user message inside the loop.
chat = model.start_chat(history=[])

while True:
    print(f"\n=== Gemini Call #{iteration} ===")

    # Determine which prompt to send based on the iteration.
    if iteration == 1:
        prompt_to_send = filled_prompt
    else:
        prompt_to_send = (
            "CONTINUE from where you left off. "
            "Resume exactly at the next unassigned shift-day-skill. "
            "Keep the same step-by-step reasoning and running penalty total. "
            "Do not repeat any shifts already assigned."
        )

    # Send the chosen prompt to the model. The chat object manages the history.
    response = chat.send_message(
        prompt_to_send,
        generation_config={"temperature": 0.3}
    )

    output = response.text
    print("\n=== PARTIAL OUTPUT ===\n")
    print(output)

    # Save chunk
    part_file = f"output_gemini_part_{iteration}.txt"
    with open(part_file, "w") as f:
        f.write(output)
    print(f"\n✅ Saved partial output to {part_file}")

    full_output += output + "\n"

    if re.search(r"CONTINUATION\b", output, re.IGNORECASE):
        print("\n🔄 CONTINUATION detected → resuming...")
        iteration += 1
    else:
        print("\n✅ No CONTINUATION found. Gemini run complete!")
        break

# Save final output
final_file = "output_gemini_combined.txt"
with open(final_file, "w") as f:
    f.write(full_output)
print(f"\n✅ Saved final combined output to {final_file}")