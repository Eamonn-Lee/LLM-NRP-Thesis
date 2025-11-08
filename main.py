import sys
from string import Template
from dotenv import load_dotenv
from util import init

from api_llm.anthropic import AnthropicLLM
from api_llm.gemini import GeminiLLM
from api_llm.openai import OpenAILLM
from api_llm.mistral import MistralLLM

DEFAULT_INSTANCE = "n005w4_0_1-2-3-3"
CONSTRAINT_FILE = "constraints_nl.txt"
#CONSTRAINT_FILE = "constraints_mm.txt"


def shared_setup(instance: str):
    # load env once
    load_dotenv("config.env")

    # load shared prompt files once
    with open("prompt_nl.txt", "r") as f:
        template_text = f.read()

    with open(CONSTRAINT_FILE, "r") as f:
        constraint_text = f.read()

    files = init(instance)

    with open(files["his"], "r") as f:
        his = f.read()
    with open(files["sce"], "r") as f:
        sce = f.read()
    with open(files["week"][0], "r") as f:
        wk0 = f.read()

    prompt = Template(template_text)
    filled_prompt = prompt.substitute(
        scenario=sce,
        history=his,
        week=wk0
    )

    print("Shared setup fin")
    print(f"INSTANCE: {instance}")

    return filled_prompt, constraint_text


if __name__ == "__main__":
    instance = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INSTANCE
    filled_prompt, constraint = shared_setup(instance)

    llms = []

    #Try build llm's, skip if fail
    for LLMCls in [AnthropicLLM, GeminiLLM, OpenAILLM, MistralLLM]:
        try:
            llm = LLMCls(filled_prompt, constraint)
            llms.append(llm)
        except RuntimeError as e:
            print(f"Skip {LLMCls.__name__}: {e}")

    # run in order
    for llm in llms:
        try:
            llm.run()
        except Exception as e:
            print(f"FAIL: {e}")

    print("Finish")
