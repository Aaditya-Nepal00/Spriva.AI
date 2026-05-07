"""
backend/agent/core.py
---------------------
The main Gemini agent brain for Spriva AI.
Handles all communication with Gemini 2.0 Flash — grant discovery,
eligibility scoring prompts, and full application drafting.
"""

import json
import re

from google import genai
from google.genai import types

from backend.config import settings

# ---------------------------------------------------------------------------
# Instantiate a module-level Gemini client — shared across all agent instances
# ---------------------------------------------------------------------------
client = genai.Client(api_key=settings.GEMINI_API_KEY)


class SprivaAgent:
    """
    Core Gemini 2.0 Flash agent for Spriva AI.

    Maintains a persistent chat session so the model retains context
    across multiple turns within a single user session. Each public
    method builds a structured prompt and returns parsed output so
    callers never have to touch raw LLM text.
    """

    def __init__(self):
        # ---------------------------------------------------------------
        # Use the module-level client; store model name and generation
        # settings that will be passed to each chat session.
        # ---------------------------------------------------------------
        self.client = client
        self.model_name = "gemini-2.5-flash"

        # Chat session is created lazily on the first message
        self.chat_session = None

        # System prompt establishes the agent's persona and constraints
        self.system_prompt = (
            "You are Spriva, an expert AI grant funding assistant for "
            "nonprofits and NGOs. You help organizations find grants they "
            "are eligible for, score eligibility, draft professional grant "
            "applications, track deadlines, and coordinate funder outreach. "
            "Always be specific, practical, and results-focused. When asked "
            "to return JSON, return only valid JSON with no extra text."
        )

    # -----------------------------------------------------------------------
    # Session management
    # -----------------------------------------------------------------------

    def start_chat(self):
        """
        Opens a new Gemini chat session with the system prompt passed via
        GenerateContentConfig — the idiomatic approach in google-genai.
        """
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )

    # -----------------------------------------------------------------------
    # Low-level messaging
    # -----------------------------------------------------------------------

    async def send_message(self, message: str) -> str:
        """
        Send a plain text message to the active chat session.

        Lazily initialises the session if it does not yet exist.

        Args:
            message: The user-facing prompt to send.

        Returns:
            The model's raw text response.
        """
        if self.chat_session is None:
            self.start_chat()

        response = self.chat_session.send_message(message)
        return response.text

    # -----------------------------------------------------------------------
    # Grant discovery
    # -----------------------------------------------------------------------

    async def run_grant_search(self, org_profile: dict) -> list:
        """
        Ask Gemini to surface six real grant opportunities that match the
        organisation's profile and return them as a structured list.

        Args:
            org_profile: Dict with keys — name, mission, focus_areas,
                         location, budget.

        Returns:
            A list of up to 6 grant dicts, or an empty list on parse failure.
        """
        name        = org_profile.get("name", "")
        mission     = org_profile.get("mission", "")
        focus_areas = org_profile.get("focus_areas", "")
        location    = org_profile.get("location", "")
        budget      = org_profile.get("budget", "")

        prompt = (
            f"Find 6 real grant opportunities for this organization:\n"
            f"Name: {name}\n"
            f"Mission: {mission}\n"
            f"Focus Areas: {focus_areas}\n"
            f"Location: {location}\n"
            f"Annual Budget: {budget}\n\n"
            "Return ONLY a JSON array with 6 grants. Each grant must have:\n"
            "- title (string)\n"
            "- funder (string)\n"
            "- amount (string, e.g. 'Up to $50,000')\n"
            "- deadline (string)\n"
            "- eligibility_score (integer 0-100)\n"
            "- description (string, 2-3 sentences)\n"
            "- application_url (string)\n"
            "- why_good_fit (string, 1-2 sentences)\n\n"
            "Return only the JSON array, no other text."
        )

        response = await self.send_message(prompt)

        # Extract the JSON array even if the model wraps it in markdown fences
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found in model response.")
            grants = json.loads(match.group())
            return grants
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"[SprivaAgent] grant search parse error: {exc}")
            return []

    # -----------------------------------------------------------------------
    # Application drafting
    # -----------------------------------------------------------------------

    async def draft_application(self, org_profile: dict, grant: dict) -> dict:
        """
        Generate a full, section-by-section grant application draft.

        Args:
            org_profile: Dict with at least keys — name, mission.
            grant:       Dict with at least keys — title, funder, amount.

        Returns:
            A dict with seven application section keys, or a dict containing
            an 'error' key if the response could not be parsed.
        """
        org_name     = org_profile.get("name", "")
        org_mission  = org_profile.get("mission", "")
        grant_title  = grant.get("title", "")
        grant_funder = grant.get("funder", "")
        grant_amount = grant.get("amount", "")

        prompt = (
            f"Draft a complete grant application for:\n"
            f"Organization: {org_name}\n"
            f"Mission: {org_mission}\n"
            f"Grant: {grant_title} by {grant_funder}\n"
            f"Grant Amount: {grant_amount}\n\n"
            "Return ONLY a JSON object with these exact keys:\n"
            "- executive_summary (2 paragraphs)\n"
            "- organization_background (2 paragraphs)\n"
            "- project_description (3 paragraphs)\n"
            "- goals_and_objectives (list of 4 specific goals)\n"
            "- budget_narrative (1 paragraph)\n"
            "- evaluation_plan (1 paragraph)\n"
            "- conclusion (1 paragraph)\n\n"
            "Return only the JSON object, no other text."
        )

        response = await self.send_message(prompt)

        # Extract the JSON object even if wrapped in markdown fences
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in model response.")
            application = json.loads(match.group())
            return application
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"[SprivaAgent] application draft parse error: {exc}")
            return {"error": f"Failed to parse application draft: {exc}"}


# ---------------------------------------------------------------------------
# Module-level singleton — import this wherever the agent is needed
# ---------------------------------------------------------------------------
agent = SprivaAgent()
