from app.services.llm_service import query_llm_overview

PROMPT_TEMPLATE = """
You are a guide. Based on Chiron in House {house} and Sign {sign}, 
generate an **overview summary** of the wound and healing journey.

Important Instruction:
- The **House** represents the *life area where the wound is expressed*.  
- The **Sign** shows the *pattern or nature of how this wound occurs*.  
- The data provided in the context is separated by Sign and House, but you must **synthesize and combine both dimensions** to create a unified interpretation.  
- Each output should reflect both the *sign’s wound style* and the *house’s life domain*, producing integrated insights rather than treating them separately.  

Output must be a **valid JSON object** with:
- "description": "A reflective overview of this placement’s emotional and spiritual themes.(50 words)"
- "coreWoundsAndEmotionalThemes": ["keywords that capture deep emotional wounds, e.g., abandonment, betrayal, etc."]
- "patternsAndStruggles": ["Five or Seven keywords that reflect common behavioral or emotional struggles."]
- "healingAndTransformation": ["Five or Seven keywords that represent the healing path and emotional growth."]
- "spiritualWisdomAndGifts": ["Five or Seven keywords showing the spiritual gifts and insights gained through healing."]
- "woundPoints": ["Write Five or Seven emotional facts or experiences that often come with this Chiron placement."]
- "patternsConnectedToThisWound": ["Describe Five or Seven behavioral or relational patterns that are shaped by this wound."]
- "healingBenefits": ["List Five or Seven healing outcomes — personal growth, peace, transformation — that come from facing and healing this wound."]
- "reflectiveQuestions": ["Six Likert-scale, close-ended questions ( the answer format is don't need to add in response Strongly Agree, Agree, Neutral, Disagree, Strongly Disagree) asking: 'How did this reading resonate with your sign and house placement?' Each question should confirm themes of wounds, struggles, and healing resonance."]

Context:
{context}

Notes for writing:
                    - For `description`: Provide a brief but emotionally deep overview of the Chiron wound and healing potential.
                    - For keyword sections: Only list **relevant themes as short phrases**.
                    - For bullet-point sections: Create **natural-sounding, insightful sentences** that reflect lived emotional experience.
                    - For the meditation name exactly as given in the context. Do not change, rewrite, or invent new names.
"""


def generate_overview(context: str, sign: str, house: str, language: str):
    prompt = PROMPT_TEMPLATE.format(context=context, sign=sign, house=house)
    data = query_llm_overview(prompt)
    if not data:
        return None

    return {
        "description": data.get("description", ""),
        "coreWoundsAndEmotionalThemes": data.get("coreWoundsAndEmotionalThemes", []),
        "patternsAndStruggles": data.get("patternsAndStruggles", []),
        "healingAndTransformation": data.get("healingAndTransformation", []),
        "spiritualWisdomAndGifts": data.get("spiritualWisdomAndGifts", []),
        "woundPoints": data.get("woundPoints", []),
        "patternsConnectedToThisWound": data.get("patternsConnectedToThisWound", []),
        "healingBenefits": data.get("healingBenefits", []),
        "reflectiveQuestions": data.get("reflectiveQuestions", []),

    }

   

