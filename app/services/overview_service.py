from app.services.llm_service import query_llm_overview

PROMPT_TEMPLATE = """
You are a guide. Based on Chiron in House {house} and Sign {sign}, 
generate an **overview summary** of the wound and healing journey.

Output must be a **valid JSON object** with:
- "description": "A reflective overview of this placement’s emotional and spiritual themes."
- "coreWoundsAndEmotionalThemes": ["keywords that capture deep emotional wounds, e.g., abandonment, betrayal, etc."]
- "patternsAndStruggles": ["keywords that reflect common behavioral or emotional struggles."]
- "healingAndTransformation": ["keywords that represent the healing path and emotional growth."]
- "spiritualWisdomAndGifts": ["keywords showing the spiritual gifts and insights gained through healing."]
- "woundPoints": ["Write 3–4 emotional facts or experiences that often come with this Chiron placement."]
- "patternsConnectedToThisWound": ["Describe 3–4 behavioral or relational patterns that are shaped by this wound."]
- "healingBenefits": ["List 3–4 healing outcomes — personal growth, peace, transformation — that come from facing and healing this wound."]

Context:
{context}

Notes for writing:
                    - For `description`: Provide a brief but emotionally deep overview of the Chiron wound and healing potential.
                    - For keyword sections: Only list **relevant themes as short phrases**.
                    - For bullet-point sections: Create **natural-sounding, insightful sentences** that reflect lived emotional experience.
"""


def generate_overview(context: str, sign: str, house: str):
    prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
    data = query_llm_overview(prompt)
    print("data-->",data)
    if not data:
        return None

    # Normalize structure
    return {
        "description": data.get("description", ""),
        "coreWoundsAndEmotionalThemes": data.get("coreWoundsAndEmotionalThemes", []),
        "patternsAndStruggles": data.get("patternsAndStruggles", []),
        "healingAndTransformation": data.get("healingAndTransformation", []),
        "spiritualWisdomAndGifts": data.get("spiritualWisdomAndGifts", []),
        "woundPoints": data.get("woundPoints", []),
        "patternsConnectedToThisWound": data.get("patternsConnectedToThisWound", []),
        "healingBenefits": data.get("healingBenefits", []),

    }

   

