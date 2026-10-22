from pydantic import BaseModel, Field
from typing import Literal

class AnalyzeRequest(BaseModel):
    transcript: str = Field(min_length=10, max_length=12000)
    user_interests: list[str] = Field(default_factory=list, max_length=30)
    user_goal: str = Field(default="discover useful content", max_length=300)
    language: str = Field(default="auto", max_length=30)

class Scores(BaseModel):
    relevance: float = Field(ge=0, le=1)
    substance: float = Field(ge=0, le=1)
    evidence_quality: float = Field(ge=0, le=1)
    originality: float = Field(ge=0, le=1)
    clarity: float = Field(ge=0, le=1)

class AnalyzeResponse(BaseModel):
    topic_tags: list[str]
    summary: str
    scores: Scores
    needs_fact_check: bool
    uncertainty: Literal["low", "medium", "high"]
    reasons: list[str]
    limitations: list[str]
    model_mode: Literal["rules_baseline"]
