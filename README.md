# Feedback Agent (MVP)

## 1. Project Overview
- 이 서비스는 개발자가 작성한 블로그 글을 분석해 **작성 스타일, 강점/약점, 구조적 품질**을 평가하고 다음 글을 위한 구체적 가이드를 제공합니다.
- **하지 않는 것**: 글을 재작성하거나 새로운 내용을 생성하지 않습니다. 레이아웃 생성도 하지 않습니다.
- **존재 이유**: Spring Boot 기반의 메인 서비스에서 글 분석을 분리해 확장성과 유지보수성을 높이기 위한 독립적인 피드백 에이전트입니다.

## 2. Architecture Overview
- **역할**: 글 분석 전용 FastAPI 서비스로, 요청을 받아 구조화된 피드백을 반환합니다.
- **Spring Boot와의 관계**: Spring Boot가 사용자 요청을 처리하고, 본 에이전트는 REST API로 호출되어 분석 결과를 반환합니다.
- **분리 이유**: AI 분석 로직을 별도 서비스로 유지하면 배포/스케일링/실험을 독립적으로 수행할 수 있고, 추후 다른 에이전트(레이아웃/작성) 추가가 용이합니다.

## 3. Tech Stack
- **Python**: 3.11+
- **FastAPI**: API 서버
- **Pydantic**: 요청/응답 스키마 검증
- **httpx**: OpenAI-compatible LLM 호출

## 4. Project Structure
```
app/
  api/            # FastAPI 라우팅 (Feedback Agent 엔드포인트)
  models/         # Pydantic 요청/응답 모델
  services/       # 에이전트 로직 및 LLM 클라이언트
  main.py         # FastAPI 앱 엔트리 포인트
```

## 5. How to Run the Server (Local)
### 1) 가상환경 생성
```bash
python -m venv .venv
```

### 2) 가상환경 활성화
```bash
source .venv/bin/activate
```

### 3) 의존성 설치
```bash
pip install -r requirements.txt
```

### 4) 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5) 예상 콘솔 출력
```bash
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 6. API Usage Guide
### Endpoint
- **Method**: POST
- **Path**: `/agents/feedback/analyze`

### Request JSON 예시
```json
{
  "request_id": "req-123",
  "user_id": "user-42",
  "post_type": "TIL",
  "content": "이 글은 오늘 학습한 내용을 정리한 글입니다...",
  "metadata": {
    "experience_level": "BEGINNER",
    "preferred_tone": "NEUTRAL"
  }
}
```

### Response JSON 예시
```json
{
  "request_id": "req-123",
  "agent": "feedback",
  "analysis": {
    "writing_style": {
      "tone": "NEUTRAL",
      "clarity_score": 0.74,
      "structure_score": 0.62,
      "depth_score": 0.58
    },
    "strengths": ["핵심 개념을 먼저 요약해 독자 진입장벽을 낮춤"],
    "weaknesses": ["문제 해결 과정의 단계별 근거가 부족함"]
  },
  "guidelines": {
    "next_article_focus": ["결론에 도달한 이유를 단계별로 설명"],
    "questions_to_answer": ["대안과 비교했을 때 선택한 이유는?"],
    "structural_advice": ["문제-가정-검증-결과 구조로 정리"]
  },
  "agent_reasoning": {
    "decision_summary": "핵심 개념은 명확하나 과정 근거가 부족해 깊이 점수가 낮음",
    "confidence": 0.66
  }
}
```

### 주요 필드 설명
- `analysis.writing_style`: 톤과 명확성/구조/깊이 점수(0~1)를 제공합니다.
- `strengths` / `weaknesses`: 관찰 기반의 구체적인 강점/약점을 나열합니다.
- `guidelines`: 다음 글에서 개선할 초점과 질문, 구조적 제안을 제공합니다.
- `agent_reasoning`: 판단 근거 요약과 신뢰도 점수를 제공합니다.

## 7. How to Test the API
### 1) curl로 호출
```bash
curl -X POST http://localhost:8000/agents/feedback/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req-123",
    "user_id": "user-42",
    "post_type": "TIL",
    "content": "이 글은 오늘 학습한 내용을 정리한 글입니다...",
    "metadata": {
      "experience_level": "BEGINNER",
      "preferred_tone": "NEUTRAL"
    }
  }'
```

### 2) Swagger UI
- 브라우저에서 `http://localhost:8000/docs` 접속
- `POST /agents/feedback/analyze` 선택 후 요청 본문 입력

## 8. Design Notes
- **무상태(stateless)**: 사용자 데이터를 저장하지 않아 운영 복잡도를 낮추고 확장성을 확보합니다.
- **구조화된 JSON 응답**: Spring Boot와의 통합이 단순해지고, 후속 처리(저장/렌더링/분석)가 쉬워집니다.
- **확장성**: 동일한 구조로 레이아웃/작성 에이전트를 추가해 멀티 에이전트 체계를 구성할 수 있습니다.

## 9. Future Extensions
- **Layout Agent**: 글의 구조와 섹션 구성에 대한 피드백 제공
- **Writing Agent**: 문장 단위 개선 방향 제시(재작성 없이 가이드 제공)
- 멀티 에이전트로 확장하여 글 작성 전체 사이클을 단계별로 지원
