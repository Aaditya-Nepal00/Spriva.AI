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
client = genai.Client(
    vertexai=True,
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION,
)


class SprivaAgent:
    """
    Core Gemini 2.5 Flash agent for Spriva AI.

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
            "You are Spriva, a Global Strategic Grant Scout. "
            "IMPORTANT: Your responses must be ultra-concise and conversational. "
            "NEVER write long paragraphs or essays. "
            "Use clear bullet points and leave an empty line between each item. "
            "Always include official clickable website links as [Name](URL). "
            "If asked for research, provide a list of max 4-5 results with 1-2 sentences each. "
            "Use double spacing between sections to keep the UI clean and readable."
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
                temperature=0.0,  # Lower temperature for more factual research
                max_output_tokens=8192,
                tools=[types.Tool(google_search=types.GoogleSearch())],
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
        Two-Step Discovery:
        1. Live Research: Use Google Search to find real grants in text format.
        2. Structured Extraction: Convert that research into strict JSON.
        """
        name        = org_profile.get("name", "")
        mission     = org_profile.get("mission", "")
        focus_areas = org_profile.get("focus_areas", "")
        location    = org_profile.get("location", "")
        budget      = org_profile.get("budget", "")

        # --- STEP 1: Live Research (Text Output) ---
        search_prompt = (
            f"You are a Global Strategic Grant Scout. Use Google Search to find 6 REAL, CURRENT grant opportunities for this organization:\n"
            f"Organization: {name}\n"
            f"Mission: {mission}\n"
            f"Focus Areas: {focus_areas}\n"
            f"Location: {location}\n"
            f"Annual Budget: {budget}\n\n"
            "CRITICAL REQUIREMENT: Do not limit yourself to local Nepal-based grants. "
            "You MUST find at least 3 opportunities from major INTERNATIONAL foundations (e.g., Bill & Melinda Gates Foundation, Ford Foundation, USAID, "
            "UN agencies, Rockefeller Foundation, or large global educational trusts) that fund projects in developing nations or education globally. "
            "Search for 'Global Education Innovation Grants' and 'International Rural Development Funds'. "
            "For each grant, find: title, funder, amount, deadline, description, website, and a contact email if possible."
        )

        try:
            print(f"[SprivaAgent] Step 1: Performing live research...")
            search_response = self.client.models.generate_content(
                model=self.model_name,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.0,
                ),
            )
            
            research_data = search_response.text
            if not research_data:
                raise ValueError("No research data found.")

            # --- STEP 2: Structured Extraction (Strict JSON Mode) ---
            print(f"[SprivaAgent] Step 2: Structuring research into JSON...")
            extract_prompt = (
                f"Extract the 6 grant opportunities from the following research data into a JSON array:\n\n"
                f"{research_data}\n\n"
                "Each object MUST have these keys: "
                "id, title, funder, amount_text, deadline, description, application_url, "
                "funder_website, funder_email, program_officer, funder_description, why_good_fit."
            )

            extraction_response = self.client.models.generate_content(
                model=self.model_name,
                contents=extract_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.0,
                ),
            )
            
            grants = json.loads(extraction_response.text)
            return grants

        except Exception as exc:
            print(f"[SprivaAgent] grant discovery error: {exc}")
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
