from pydantic import BaseModel
from typing import List

class OverviewResponse(BaseModel):
    sign: str
    house: str
    description: str
    coreWoundsAndEmotionalThemes: List[str]
    patternsAndStruggles: List[str]
    healingAndTransformation: List[str]
    spiritualWisdomAndGifts: List[str]
    woundPoints: List[str]
    patternsConnectedToThisWound: List[str]
    healingBenefits: List[str]
    
