import os
from .base import BaseLLMClient
import google.generativeai as genai

class GeminiLLM(BaseLLMClient):
    name = "gemini"

    def __init__(self, filled_prompt: str, constraint: str):
        super().__init__(filled_prompt, constraint)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.genai = genai
        self.model_name = "gemini-2.0-flash"

    def _init_state(self):
        model = self.genai.GenerativeModel(
            self.model_name,
            system_instruction=self.constraint
        )
        chat = model.start_chat(history=[])

        return {"chat": chat}

    def _run_once(self, prompt: str, state, iteration: int):
        chat = state["chat"]

        resp = chat.send_message(
            prompt,
            generation_config={"temperature": 0.3},
        )
        output = resp.text

        return output, state