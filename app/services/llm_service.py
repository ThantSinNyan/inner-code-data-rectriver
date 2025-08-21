import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

print("api-key -->", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a healing guide. Based on Chiron in House {house} and Sign {sign}, 
create a structured **day-by-day healing plan** in JSON format.

For each day include:
- day (Day 1, Day 2, …)
- overview (short explanation of healing focus)
- activity (title of activity)
- prompts (unique list of journaling prompts)
- meditation (title of meditation)

Context:
{context}

Make sure the JSON is valid and remove duplicate prompts.
"""

def clean_json_response(text: str) -> str:
    """
    Remove Markdown fences and extract JSON.
    """
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    start = text.find("[")  # now expecting a list
    end = text.rfind("]") + 1
    if start == -1 or end == -1:
        return None
    return text[start:end]

def query_llm(context: str, sign: str, house: str):
    try:
        prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        print("LLM raw response:", content[:500])

        clean_content = clean_json_response(content)
        if not clean_content:
            print("Could not extract JSON from LLM response")
            return None

        data = json.loads(clean_content)

        # Ensure every item has the required keys
        plan_list = []
        for item in data:
            plan_list.append({
                "day": item.get("day", ""),
                "overview": item.get("overview", ""),
                "activity": item.get("activity", ""),
                "prompts": item.get("prompts", []),
                "meditation": item.get("meditation", "")
            })
        return plan_list

    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return None
    except Exception as e:
        print("LLM query error:", e)
        return None