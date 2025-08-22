import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Switch to faster model
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

PROMPT_TEMPLATE = """
You are a healing guide. Based on Chiron in House {house} and Sign {sign}, identify the main wound points for this placement and create a **day-by-day healing plan**.

Output must be in **valid JSON array** format only.

Each item in the array represents one day and must include:
- "day": (string, e.g., "Day 1")
- "overview": (string, detailed explanation of the healing focus: what the wound is, why healing is needed, and the benefit of this day’s practice)
- "activity": (string, title of the main activity)
- "prompts": (array of unique journaling prompts, no duplicates)
- "meditation": (string, title of a meditation practice)

Context:
{context}

Make sure the JSON is valid and remove duplicate prompts.
"""


def clean_json_response(text: str) -> str:
    """Extract JSON array from LLM text."""
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == -1:
        return None
    return text[start:end]


def query_llm(context: str, sign: str, house: str):
    try:
        prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        print("LLM raw response:", content[:200])

        clean_content = clean_json_response(content)
        if not clean_content:
            return None

        data = json.loads(clean_content)
        return [
            {
                "day": item.get("day", ""),
                "overview": item.get("overview", ""),
                "activity": item.get("activity", ""),
                "prompts": item.get("prompts", []),
                "meditation": item.get("meditation", "")
            }
            for item in data
        ]

    except Exception as e:
        print("LLM query error:", e)
        return None

