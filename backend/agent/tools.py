"""
backend/agent/tools.py
----------------------
Tool definitions for the Gemini agent.
These dicts follow the Gemini function calling schema so the model
understands what external tools and actions it has available to use.
"""

from typing import Any
from backend.grants.search import grant_search
from backend.grants.scorer import scorer
from backend.agent.prompts import (
    grant_search_prompt,
    application_draft_prompt,
    score_reasoning_prompt,
    followup_email_prompt,
    document_intake_prompt
)

# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------
TOOLS_REGISTRY = [
    {
        "name": "search_grants",
        "description": "Search for grant opportunities matching the organization profile",
        "parameters": {
            "type": "object",
            "properties": {
                "org_name": {"type": "string"},
                "mission": {"type": "string"},
                "focus_areas": {"type": "string"},
                "location": {"type": "string"},
                "budget": {"type": "string"}
            },
            "required": ["org_name", "mission", "focus_areas", "location", "budget"]
        }
    },
    {
        "name": "score_grant_eligibility",
        "description": "Score an organization's eligibility for a specific grant with evidence-based reasoning",
        "parameters": {
            "type": "object",
            "properties": {
                "org_name": {"type": "string"},
                "grant_title": {"type": "string"},
                "grant_funder": {"type": "string"},
                "grant_amount": {"type": "string"},
                "grant_description": {"type": "string"},
                "org_focus_areas": {"type": "string"},
                "org_location": {"type": "string"},
                "org_budget": {"type": "string"}
            },
            "required": ["org_name", "grant_title", "grant_funder", "grant_amount", "grant_description", "org_focus_areas", "org_location", "org_budget"]
        }
    },
    {
        "name": "draft_application",
        "description": "Draft a complete grant application for a specific grant opportunity",
        "parameters": {
            "type": "object",
            "properties": {
                "org_name": {"type": "string"},
                "org_mission": {"type": "string"},
                "grant_title": {"type": "string"},
                "grant_funder": {"type": "string"},
                "grant_amount": {"type": "string"}
            },
            "required": ["org_name", "org_mission", "grant_title", "grant_funder", "grant_amount"]
        }
    },
    {
        "name": "track_deadline",
        "description": "Add a grant deadline to Google Calendar",
        "parameters": {
            "type": "object",
            "properties": {
                "grant_title": {"type": "string"},
                "funder_name": {"type": "string"},
                "deadline_date": {"type": "string"},
                "org_name": {"type": "string"}
            },
            "required": ["grant_title", "funder_name", "deadline_date", "org_name"]
        }
    },
    {
        "name": "send_funder_outreach",
        "description": "Draft and send an outreach email to a grant funder via Gmail",
        "parameters": {
            "type": "object",
            "properties": {
                "funder_email": {"type": "string"},
                "funder_name": {"type": "string"},
                "grant_title": {"type": "string"},
                "org_name": {"type": "string"},
                "org_mission": {"type": "string"}
            },
            "required": ["funder_email", "funder_name", "grant_title", "org_name", "org_mission"]
        }
    },
    {
        "name": "save_to_drive",
        "description": "Save a grant application draft to Google Drive",
        "parameters": {
            "type": "object",
            "properties": {
                "document_title": {"type": "string"},
                "document_content": {"type": "string"},
                "folder_name": {"type": "string"}
            },
            "required": ["document_title", "document_content", "folder_name"]
        }
    }
]

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_tool_names() -> list:
    """
    Returns a list containing the names of all registered tools.
    """
    return [tool["name"] for tool in TOOLS_REGISTRY]

def get_tool_by_name(name: str) -> dict:
    """
    Returns the tool dictionary that matches the given name.
    Returns None if the tool is not found.
    """
    for tool in TOOLS_REGISTRY:
        if tool["name"] == name:
            return tool
    return None
