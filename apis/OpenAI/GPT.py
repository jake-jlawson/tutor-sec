from openai import OpenAI
import os

# load environment variables
from dotenv import load_dotenv
load_dotenv()


class GPT:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def chat_completion(self, messages: list[dict]):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
