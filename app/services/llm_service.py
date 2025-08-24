import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")


def clean_json_response(text: str) -> str:
    """Extract the first valid JSON array or object from the response text."""
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # Look for array
    if "[" in text:
        start = text.find("[")
        depth = 0
        for i, ch in enumerate(text[start:], start=start):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

    # Look for object
    if "{" in text:
        start = text.find("{")
        depth = 0
        for i, ch in enumerate(text[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

    return None



def query_llm_plan(prompt: str, temperature: float = 0.3):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        content = response.choices[0].message.content.strip()
        print("LLM raw response:::", content)

        clean_content = clean_json_response(content)
        if not clean_content:
            return None

        # Load only the cleaned JSON
        return json.loads(clean_content)

    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return None
    except Exception as e:
        print("LLM query error:", e)
        return None
    
def query_llm_overview(prompt: str, temperature: float = 0.3):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        clean_content = response.choices[0].message.content.strip()
        print("LLM raw response:::", clean_content)

        
        if not clean_content:
            return None

        # Load only the cleaned JSON
        return json.loads(clean_content)

    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return None
    except Exception as e:
        print("LLM query error:", e)
        return None
