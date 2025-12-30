from __future__ import annotations

import os

from fastapi import APIRouter, status

from app.models.feedback import ErrorDetails, ErrorResponse, FeedbackRequest, FeedbackResponse
from app.services.feedback_agent import FeedbackAgent
from app.services.llm_client import OpenAICompatibleClient, StubLLMClient


feedback_router = APIRouter(prefix="/agents/feedback", tags=["feedback"])


def _build_llm_client() -> OpenAICompatibleClient | StubLLMClient:
    """
    Chooses a real model client when environment variables are present,
    otherwise falls back to a deterministic stub for bootstrapping.
    """

    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")

    if base_url and api_key and model:
        return OpenAICompatibleClient(base_url=base_url, api_key=api_key, model=model)

    return StubLLMClient(
        response_json=(
            "{"
            "\"analysis\": {"
            "\"writing_style\": {"
            "\"tone\": \"NEUTRAL\","
            "\"clarity_score\": 0.5,"
            "\"structure_score\": 0.5,"
            "\"depth_score\": 0.5"
            "},"
            "\"strengths\": [\"Stubbed response; configure LLM env vars.\"],"
            "\"weaknesses\": [\"Stubbed response; configure LLM env vars.\"]"
            "},"
            "\"guidelines\": {"
            "\"next_article_focus\": [\"Stubbed response; configure LLM env vars.\"],"
            "\"questions_to_answer\": [\"Stubbed response; configure LLM env vars.\"],"
            "\"structural_advice\": [\"Stubbed response; configure LLM env vars.\"]"
            "},"
            "\"agent_reasoning\": {"
            "\"decision_summary\": "
            "\"Stubbed response; configure LLM env vars.\","
            "\"confidence\": 0.2"
            "}"
            "}"
        )
    )


@feedback_router.post(
    "/analyze",
    response_model=FeedbackResponse | ErrorResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_feedback(payload: FeedbackRequest) -> FeedbackResponse | ErrorResponse:
    agent = FeedbackAgent(llm_client=_build_llm_client())

    try:
        agent.validate_content_length(payload.content)
        return agent.analyze(payload)
    except ValueError as exc:
        return ErrorResponse(
            request_id=payload.request_id,
            error=ErrorDetails(message=str(exc), type="validation_error"),
        )
    except Exception:
        return ErrorResponse(
            request_id=payload.request_id,
            error=ErrorDetails(
                message="Feedback analysis failed due to an internal error.",
                type="llm_error",
            ),
        )
