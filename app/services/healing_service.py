from app.services.llm_service import query_llm_plan

PROMPT_TEMPLATE = """
You are a healing guide. Based on Chiron in House {house} and Sign {sign}, identify the main wound points for this placement and create a **day-by-day healing plan**.

Output must be in **valid JSON array** format only.

Each item in the array represents one day and must include:
- "overview": (string, detailed explanation of the healing focus: what the wound is, why healing is needed, and the benefit of this day’s practice)
- "activity": (string, title of the main activity)
- "prompts": (array of unique journaling prompts, no duplicates in each day)
- "meditation": (string, title of a meditation practice)

Context:
{context}

Make sure the JSON is valid and remove duplicate prompts.
"""


def generate_healing_plan(context: str, sign: str, house: str):
    prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
    data = query_llm_plan(prompt)
    if not data:
        return None

    # Normalize structure
    return [
        {
            "overview": item.get("overview", ""),
            "activity": item.get("activity", ""),
            "prompts": item.get("prompts", []),
            "meditation": item.get("meditation", "")
        }
        for item in data
    ]
