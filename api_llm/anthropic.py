import os
from .base import BaseLLMClient
from anthropic import Anthropic

class AnthropicLLM(BaseLLMClient):
    name = "anthropic"

    def __init__(self, filled_prompt: str, constraint: str):
        super().__init__(filled_prompt, constraint)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not found.")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-opus-4-20250514"

    def _init_state(self):
        #requires new msg history
        return {"messages": []}

    def _run_once(self, prompt: str, state, iteration: int):
        #send all msgs
        if iteration == 1:
            messages = [{"role": "user", "content": prompt}]
        else:
            state["messages"].append({"role": "user", "content": prompt})
            messages = state["messages"]

        resp = self.client.messages.create(
            model=self.model,
            system=self.constraint,
            messages=messages,
            max_tokens=3600,
        )
        output = resp.content[0].text

        if iteration == 1:
            state["messages"] = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": output},
            ]
        else:
            state["messages"].append({"role": "assistant", "content": output})

        return output, state