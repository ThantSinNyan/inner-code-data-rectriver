from pydantic import BaseModel
from typing import List, Dict


class PlanRequest(BaseModel):
    sign: str
    house: str
    question: str
    language: str

class PlanEndUserRequest(BaseModel):
    birthDate: str
    birthTime: str
    birthPlace: str
    language: str

class PlanResponse(BaseModel):
    plan: list