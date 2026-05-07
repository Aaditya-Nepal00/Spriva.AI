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
from backend.elastic.search import elastic_search
from backend.agent.reasoning import reasoning_engine
from backend.grants.scorer import scorer
from backend.agent.intake import intake_agent
from backend.agent.pipeline import pipeline


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


class DocumentText(BaseModel):
    text: str
    filename: str = "document"


class MultipleDocuments(BaseModel):
    documents: list


class PipelineRequest(BaseModel):
    document_text: str
    filename: str = "document"


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
        "model": "gemini-2.5-flash",
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
    Grant discovery endpoint using Elasticsearch with eligibility scoring.
    """
    try:
        profile_data = body.model_dump()
        
        # 1. Call elasticsearch
        grants = elastic_search.search_grants(profile_data)
        
        # 2. Fallback if no results
        if not grants:
            grants = await agent.run_grant_search(profile_data)
            
        # 3 & 4. Calculate scores for each grant
        for grant in grants:
            scores = scorer.calculate_base_score(profile_data, grant)
            score = scores["total_score"]
            
            grant["eligibility_score"] = score
            grant["score_breakdown"] = scores
            grant["recommendation"] = (
                "Strong Match" if score >= 70 
                else "Good Match" if score >= 50 
                else "Weak Match"
            )
            
        # 5. Sort by eligibility score
        grants.sort(key=lambda x: x.get("eligibility_score", 0), reverse=True)
            
        return {
            "grants": grants,
            "count": len(grants),
            "status": "ok",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/grants/rank")
async def rank_grants(body: OrgProfile):
    """
    Quick ranking endpoint using Reasoning Engine.
    """
    try:
        profile_data = body.model_dump()
        grants = elastic_search.search_grants(profile_data)
        
        ranked_grants = await reasoning_engine.quick_rank(profile_data, grants)
        
        return {
            "grants": ranked_grants,
            "count": len(ranked_grants),
            "status": "ok",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/grants/reason")
async def reason_grants(body: dict):
    """
    Agent reasoning endpoint.
    """
    try:
        org_profile = body.get("org_profile")
        grants = body.get("grants")
        
        # Use the reasoning engine created earlier
        reasoning_result = await reasoning_engine.reason_over_grants(org_profile, grants)
        return reasoning_result
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


@app.post("/api/intake/text")
async def intake_text(body: DocumentText):
    """
    Processes uploaded text from a single document.
    """
    try:
        result = await intake_agent.process_uploaded_text(body.text, body.filename)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/intake/multiple")
async def intake_multiple(body: MultipleDocuments):
    """
    Processes multiple documents and merges profile information.
    """
    try:
        result = await intake_agent.process_multiple_documents(body.documents)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/pipeline/run")
async def run_pipeline(body: PipelineRequest):
    """
    Runs the full Spriva AI pipeline:
    Document Intake -> Grant Search -> Ranking -> Email Drafting.
    This is the main demo endpoint.
    """
    try:
        result = await pipeline.run_full_pipeline(body.document_text, body.filename)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/pipeline/from-profile")
async def run_pipeline_from_profile(body: OrgProfile):
    """
    Runs the pipeline starting from an existing profile.
    Grant Search -> Ranking -> Email Drafting.
    """
    try:
        result = await pipeline.get_best_grant_only(body.model_dump())
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))

