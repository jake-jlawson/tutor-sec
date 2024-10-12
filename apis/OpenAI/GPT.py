from openai import OpenAI
import os

# load environment variables
from dotenv import load_dotenv
load_dotenv()


class GPT:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
