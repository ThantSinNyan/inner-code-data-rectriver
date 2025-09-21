from app.services.llm_service import query_llm_plan

PROMPT_TEMPLATE = """
You are a healing guide. Based on Chiron in House {house} and Sign {sign}, 
identify the main wound points for this placement and create a **day-by-day healing plan**.

Important Instruction:
- The **House** represents the *life area where the wound is expressed*.  
- The **Sign** shows the *pattern or nature of how this wound occurs*.  
- The data provided in the context is separated by Sign and House, but you must **synthesize and combine both dimensions** to create a unified interpretation.  
- Each day’s plan should clearly reflect both the *sign’s wound style* and the *house’s life domain*, producing integrated insights rather than treating them separately.  

Output must be in **valid JSON array** format only.

Each item in the array represents one day and must include:
- "overview": (string, detailed explanation of the healing focus: what the wound is, why healing is needed, and the benefit of this day’s practice 50 words)
- "activity": (string, title of the main activity)
- "prompts": (array of unique journaling prompts, no duplicates in each day)
- "meditation": (string, title of a meditation practice)
- "affirmation": (short setence that is a positive affirmation that helps release or rewire negative wound patterns, transforming them into empowering and positive beliefs)

Context:
{context}

Notes for writing:
- Always merge both Sign (pattern/nature of wound) and House (life area impacted) into a single cohesive explanation (50 words).  
- For "overview": Provide a deep, reflective summary that connects the wound to the day’s healing focus.  
- For "prompts": Write insightful, open-ended journaling prompts — no duplicates within a single day.  
- For "meditation": Use the exact meditation name provided in the context (do not change or invent new ones).
- For "affirmation": Write short note insightful— no duplicates within a single day.    
- Ensure the JSON is valid and remove duplicate prompts.
"""

def generate_healing_plan(context: str, sign: str, house: str):
    prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
    data = query_llm_plan(prompt)
    if not data:
        return None

    return [
        {
            "overview": item.get("overview", ""),
            "activity": item.get("activity", ""),
            "prompts": item.get("prompts", []),
            "meditation": item.get("meditation", ""),
            "affirmation": item.get("affirmation", "")
        }
        for item in data
    ]
