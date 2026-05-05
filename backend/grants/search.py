"""
backend/grants/search.py
------------------------
Grant discovery engine for Spriva AI.
Uses the Gemini agent to search for real, active grants matching an
organization's profile or a specific focus area.
"""

import json
import re
from datetime import datetime

from backend.agent.core import agent
from backend.config import settings


class GrantSearchEngine:
    """
    Handles prompt building and JSON extraction for grant discovery tasks.
    """

    def __init__(self):
        # Use the module-level agent singleton
        self.agent = agent

    async def search_grants(self, org_profile: dict) -> list:
        """
        Discovers up to 6 real, active grants tailored to the organization.
        
        Args:
            org_profile: Dict containing name, mission, focus_areas,
                         location, and budget.
                         
        Returns:
            A list of grant dictionaries.
        """
        name = org_profile.get("name", "")
        mission = org_profile.get("mission", "")
        focus_areas = org_profile.get("focus_areas", "")
        location = org_profile.get("location", "")
        budget = org_profile.get("budget", "")
        current_date = datetime.now().strftime("%B %d, %Y")

        prompt = (
            f"You are a grant research expert. Find 6 real, currently active "
            f"grant opportunities for this nonprofit organization.\n\n"
            f"Organization: {name}\n"
            f"Mission: {mission}\n"
            f"Focus Areas: {focus_areas}\n"
            f"Location: {location}\n"
            f"Annual Budget: {budget}\n"
            f"Current Date: {current_date}\n\n"
            f"Search your knowledge for real grants from foundations, "
            f"government agencies, and corporations that match this org.\n\n"
            f"Return ONLY a valid JSON array. Each grant object must have "
            f"exactly these fields:\n"
            f"- id: unique string like 'grant_001'\n"
            f"- title: full grant program name\n"
            f"- funder: organization giving the grant\n"
            f"- funder_type: one of [Foundation, Government, Corporate, UN Agency]\n"
            f"- amount: funding range as string e.g. 'Up to $50,000'\n"
            f"- deadline: next deadline as string\n"
            f"- focus_areas: list of strings\n"
            f"- location_requirement: string\n"
            f"- description: 2-3 sentence description\n"
            f"- application_url: URL string\n"
            f"- requirements: list of 3-4 key requirements\n\n"
            f"Return ONLY the JSON array. No explanation. No markdown."
        )

        response_text = await self.agent.send_message(prompt)

        try:
            match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found in response")
            return json.loads(match.group())
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"[GrantSearchEngine] Error parsing search_grants: {exc}")
            return []

    async def get_grant_details(self, grant_id: str, grants_list: list) -> dict:
        """
        Retrieves a specific grant by its ID from a provided list of grants.
        
        Args:
            grant_id: The unique ID to search for.
            grants_list: The list of grant dictionaries to search within.
            
        Returns:
            The grant dictionary if found, otherwise an empty dict.
        """
        for grant in grants_list:
            if grant.get("id") == grant_id:
                return grant
        return {}

    async def search_by_focus_area(self, focus_area: str, location: str = "Global") -> list:
        """
        Simplified search to find 4 grants based primarily on a focus area.
        
        Args:
            focus_area: The core topic (e.g., 'Climate Change', 'Education').
            location: The target region (defaults to 'Global').
            
        Returns:
            A list of up to 4 grant dictionaries.
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = (
            f"You are a grant research expert. Find 4 real, currently active "
            f"grant opportunities for nonprofits working in:\n"
            f"Focus Area: {focus_area}\n"
            f"Location: {location}\n"
            f"Current Date: {current_date}\n\n"
            f"Return ONLY a valid JSON array. Each grant object must have "
            f"exactly these fields:\n"
            f"- id: unique string like 'grant_001'\n"
            f"- title: full grant program name\n"
            f"- funder: organization giving the grant\n"
            f"- funder_type: one of [Foundation, Government, Corporate, UN Agency]\n"
            f"- amount: funding range as string\n"
            f"- deadline: next deadline as string\n"
            f"- focus_areas: list of strings\n"
            f"- location_requirement: string\n"
            f"- description: 2-3 sentence description\n"
            f"- application_url: URL string\n"
            f"- requirements: list of 3-4 key requirements\n\n"
            f"Return ONLY the JSON array. No explanation. No markdown."
        )

        response_text = await self.agent.send_message(prompt)

        try:
            match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found in response")
            return json.loads(match.group())
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"[GrantSearchEngine] Error parsing search_by_focus_area: {exc}")
            return []


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
grant_search = GrantSearchEngine()
