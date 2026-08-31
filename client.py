import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL")

client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key="ollama"
)

LLM_MODEL = os.getenv("LLM_MODEL")
with open("ask.md", "r", encoding="utf-8") as f:
    ASK_PROMPT = f.read()


def call_model(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
