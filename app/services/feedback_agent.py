from __future__ import annotations

from dataclasses import dataclass

from app.models.feedback import (
    FeedbackAnalysis,
    FeedbackGuidelines,
    FeedbackRequest,
    FeedbackResponse,
    LLMStructuredOutput,
    parse_llm_output,
)
from app.services.llm_client import LLMClient


MIN_CONTENT_LENGTH = 120
MAX_CONTENT_LENGTH = 12000


@dataclass
class FeedbackAgent:
    """
    Encapsulates feedback generation so the API layer remains thin
    and can later swap the implementation without touching routing.
    """

    llm_client: LLMClient

    def analyze(self, request: FeedbackRequest) -> FeedbackResponse:
        prompt = self._build_prompt(request)
        raw_output = self.llm_client.complete(prompt)
        structured = parse_llm_output(raw_output)
        return FeedbackResponse(
            request_id=request.request_id,
            analysis=structured.analysis,
            guidelines=structured.guidelines,
            agent_reasoning=structured.agent_reasoning,
        )

    @staticmethod
    def validate_content_length(content: str) -> None:
        length = len(content)
        if length < MIN_CONTENT_LENGTH:
            raise ValueError(
                "content is too short for meaningful feedback; "
                f"minimum length is {MIN_CONTENT_LENGTH} characters"
            )
        if length > MAX_CONTENT_LENGTH:
            raise ValueError(
                "content is too long for analysis; "
                f"maximum length is {MAX_CONTENT_LENGTH} characters"
            )

    def _build_prompt(self, request: FeedbackRequest) -> str:
        """
        The prompt is explicit about the output schema to ensure the result
        can be parsed deterministically into Pydantic models.
        """

        return (
            "You are reviewing a developer blog post. Analyze writing style, "
            "strengths, weaknesses, and provide actionable guidance for the NEXT article. "
            "Do NOT rewrite or add new content. Avoid generic feedback. "
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            "  \"analysis\": {\n"
            "    \"writing_style\": {\n"
            "      \"tone\": \"CASUAL|NEUTRAL|TECHNICAL\",\n"
            "      \"clarity_score\": 0.0-1.0,\n"
            "      \"structure_score\": 0.0-1.0,\n"
            "      \"depth_score\": 0.0-1.0\n"
            "    },\n"
            "    \"strengths\": [\"string\"],\n"
            "    \"weaknesses\": [\"string\"]\n"
            "  },\n"
            "  \"guidelines\": {\n"
            "    \"next_article_focus\": [\"string\"],\n"
            "    \"questions_to_answer\": [\"string\"],\n"
            "    \"structural_advice\": [\"string\"]\n"
            "  },\n"
            "  \"agent_reasoning\": {\n"
            "    \"decision_summary\": \"string\",\n"
            "    \"confidence\": 0.0-1.0\n"
            "  }\n"
            "}\n\n"
            f"Post type: {request.post_type}\n"
            f"User level: {request.metadata.experience_level}\n"
            f"Preferred tone: {request.metadata.preferred_tone}\n"
            "Content:\n"
            f"{request.content}\n"
        )
