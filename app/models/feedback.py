from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, ValidationError, field_validator


class PostType(str, Enum):
    TIL = "TIL"
    RETROSPECTIVE = "RETROSPECTIVE"
    TROUBLESHOOTING = "TROUBLESHOOTING"
    DESIGN = "DESIGN"


class ExperienceLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class PreferredTone(str, Enum):
    CASUAL = "CASUAL"
    NEUTRAL = "NEUTRAL"
    TECHNICAL = "TECHNICAL"


class FeedbackMetadata(BaseModel):
    experience_level: ExperienceLevel
    preferred_tone: PreferredTone


class FeedbackRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    post_type: PostType
    content: str = Field(..., min_length=1)
    metadata: FeedbackMetadata

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class WritingStyle(BaseModel):
    tone: PreferredTone
    clarity_score: float = Field(..., ge=0.0, le=1.0)
    structure_score: float = Field(..., ge=0.0, le=1.0)
    depth_score: float = Field(..., ge=0.0, le=1.0)


class FeedbackAnalysis(BaseModel):
    writing_style: WritingStyle
    strengths: List[str]
    weaknesses: List[str]


class FeedbackGuidelines(BaseModel):
    next_article_focus: List[str]
    questions_to_answer: List[str]
    structural_advice: List[str]


class AgentReasoning(BaseModel):
    decision_summary: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class FeedbackResponse(BaseModel):
    request_id: str
    agent: str = Field(default="feedback")
    analysis: FeedbackAnalysis
    guidelines: FeedbackGuidelines
    agent_reasoning: AgentReasoning


class ErrorDetails(BaseModel):
    message: str
    type: str


class ErrorResponse(BaseModel):
    request_id: str
    agent: str = Field(default="feedback")
    error: ErrorDetails


class LLMStructuredOutput(BaseModel):
    analysis: FeedbackAnalysis
    guidelines: FeedbackGuidelines
    agent_reasoning: AgentReasoning


def parse_llm_output(payload: str) -> LLMStructuredOutput:
    try:
        return LLMStructuredOutput.model_validate_json(payload)
    except ValidationError as exc:
        raise ValueError("LLM output failed validation") from exc
