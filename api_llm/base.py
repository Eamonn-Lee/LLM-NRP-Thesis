import re

CONTINUATION_PROMPT = (
    "CONTINUE from where you left off. "
    "Resume exactly at the next unassigned shift-day-skill. "
    "Keep the same step-by-step reasoning and running penalty total. "
    "Do not repeat any shifts already assigned."
)


class BaseLLMClient:
    name = "base"

    def __init__(self, filled_prompt: str, constraint: str):
        self.filled_prompt = filled_prompt
        self.constraint = constraint

    def has_continuation(self, text: str) -> bool:
        return bool(re.search(r"CONTINUATION\b", text, re.IGNORECASE))

    def run(self):
        print(f"\nRun {self.name}")

        iteration = 1
        full_output = ""
        state = self._init_state()

        while True:
            print(f"{self.name} Call #{iteration}")

            if iteration == 1:
                prompt_to_send = self.filled_prompt
            else:
                prompt_to_send = CONTINUATION_PROMPT

            output, state = self._run_once(prompt_to_send, state, iteration)

            print(f"[{self.name} partial output]\n")
            print(output)

            part_file = f"output_{self.name}_part_{iteration}.txt"
            with open(part_file, "w") as f:
                f.write(output)
            print(f"Saved {part_file}")

            full_output += output + "\n"

            if self.has_continuation(output):
                print(f"{self.name} CONTINUATION found -> newcall")
                iteration += 1
            else:
                print(f"{self.name} finish")
                break

        final_file = f"output_{self.name}_combined.txt"
        with open(final_file, "w") as f:
            f.write(full_output)
        print(f"{self.name} combined written to {final_file}")

    # hooks
    def _init_state(self):
        return None

    def _run_once(self, prompt: str, state, iteration: int):
        raise NotImplementedError