from fastapi import FastAPI

from app.api.router import feedback_router


# The FastAPI application is intentionally small and composed via routers
# so we can extend to multiple agents without touching the core app object.
app = FastAPI(title="Devlog Feedback Agent", version="0.1.0")

# Single router for the Feedback Agent MVP.
app.include_router(feedback_router)
