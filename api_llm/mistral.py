import os
from .base import BaseLLMClient
from mistralai import Mistral

class MistralLLM(BaseLLMClient):
    name = "mistral"

    def __init__(self, filled_prompt: str, constraint: str):
        super().__init__(filled_prompt, constraint)
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY not found.")

        self.client = Mistral(api_key=api_key)
        self.model_name = "mistral-large-latest"

    def _init_state(self):
        return {
            "messages": [
                {"role": "system", "content": self.constraint},
            ]
        }

    def _run_once(self, prompt: str, state, iteration: int):
        state["messages"].append({"role": "user", "content": prompt})

        resp = self.client.chat.complete(
            model=self.model_name,
            messages=state["messages"],
        )
        output = resp.choices[0].message.content

        state["messages"].append({"role": "assistant", "content": output})

        return output, state
