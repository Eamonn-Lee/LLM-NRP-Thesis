import os
from .base import BaseLLMClient
from openai import OpenAI

class OpenAILLM(BaseLLMClient):
    name = "openai"

    def __init__(self, filled_prompt: str, constraint: str):
        super().__init__(filled_prompt, constraint)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found.")

        self.client = OpenAI(api_key=api_key)
        self.model_name = "gpt-4o"

    def _init_state(self):
        return {
            "messages": [
                {"role": "system", "content": self.constraint},
            ]
        }

    def _run_once(self, prompt: str, state, iteration: int):
        state["messages"].append({"role": "user", "content": prompt})

        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=state["messages"],
            temperature=0.3,
        )
        output = resp.choices[0].message.content

        state["messages"].append({"role": "assistant", "content": output})

        return output, state