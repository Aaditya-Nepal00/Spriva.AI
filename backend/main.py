"""
backend/main.py
---------------
FastAPI application entry point for Spriva AI.
Exposes REST endpoints for chat, grant search, and application drafting.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.agent.core import agent
from backend.config import settings


# ---------------------------------------------------------------------------
# Lifespan — runs startup/shutdown logic without the deprecated @app.on_event
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Spriva AI server started on port {settings.PORT}")
    yield  # everything after yield runs on shutdown


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Spriva AI",
    version="1.0.0",
    description="AI grant funding assistant for nonprofits and NGOs.",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — permissive for local development; tighten before production
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class OrgProfile(BaseModel):
    name: str
    mission: str
    focus_areas: str
    location: str
    budget: str


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class GrantApplicationRequest(BaseModel):
    org_profile: OrgProfile
    grant: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Health-check / welcome route. Confirms the API is reachable."""
    return {
        "status": "ok",
        "message": "Spriva AI is running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """
    Detailed health check — returns the active model name and port so
    callers can verify configuration without inspecting server logs.
    """
    return {
        "status": "healthy",
        "model": "gemini-2.0-flash",
        "port": settings.PORT,
    }


@app.post("/api/chat")
async def chat(body: ChatMessage):
    """
    General-purpose chat endpoint.

    Accepts a plain-text message and returns the agent's response.
    Useful for free-form queries or follow-up questions within a session.
    """
    try:
        response_text = await agent.send_message(body.message)
        return {"response": response_text, "status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/grants/search")
async def search_grants(body: OrgProfile):
    """
    Grant discovery endpoint.

    Accepts an organization profile and returns up to 6 matched grant
    opportunities, each with an eligibility score (0–100).
    """
    try:
        grants_list = await agent.run_grant_search(body.model_dump())
        return {
            "grants": grants_list,
            "count": len(grants_list),
            "status": "ok",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/grants/apply")
async def draft_application(body: GrantApplicationRequest):
    """
    Application drafting endpoint.

    Accepts an organization profile and a target grant dict, then returns
    a fully structured draft with seven sections ready to copy-paste.
    """
    try:
        draft = await agent.draft_application(
            body.org_profile.model_dump(),
            body.grant,
        )
        return {"application": draft, "status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
