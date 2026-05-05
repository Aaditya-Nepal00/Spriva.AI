"""
backend/grants/scorer.py
------------------------
Handles eligibility scoring for grant opportunities using a combination
of rule-based matching and Gemini-generated reasoning.
"""

import re
from backend.agent.core import agent


class EligibilityScorer:
    """
    Evaluates how well an organization's profile matches a specific grant.
    """

    def __init__(self):
        self.agent = agent
        self.scoring_criteria = {
            "mission_alignment": 30,
            "location_match": 20,
            "budget_fit": 20,
            "focus_area_match": 30
        }

    def calculate_base_score(self, org_profile: dict, grant: dict) -> dict:
        """
        Pure Python scoring logic based on text and number matching.
        Does not require any API calls.
        """
        # -------------------------------------------------------------
        # a) Mission Alignment (0-30 points)
        # -------------------------------------------------------------
        org_focus_str = str(org_profile.get("focus_areas", "")).lower()
        # Split focus areas into words longer than 3 chars for meaningful matching
        org_words = [w.strip() for w in re.split(r'[,\s]+', org_focus_str) if len(w) > 3]
        grant_desc = str(grant.get("description", "")).lower()
        
        matches = sum(1 for word in org_words if word in grant_desc)
        if matches >= 3:
            mission_score = 30
        elif matches == 2:
            mission_score = 20
        elif matches == 1:
            mission_score = 10
        else:
            mission_score = 0
            
        # -------------------------------------------------------------
        # b) Location Match (0-20 points)
        # -------------------------------------------------------------
        grant_loc = str(grant.get("location_requirement", "")).lower()
        org_loc = str(org_profile.get("location", "")).lower()
        
        global_terms = ["global", "international", "worldwide"]
        
        if any(term in grant_loc for term in global_terms):
            location_score = 20
        elif org_loc and org_loc in grant_loc:
            location_score = 20
        elif not grant_loc or grant_loc.strip() == "none" or grant_loc.strip() == "":
            location_score = 15
        else:
            location_score = 5
            
        # -------------------------------------------------------------
        # c) Budget Fit (0-20 points)
        # -------------------------------------------------------------
        budget_score = 15  # Default neutral score
        org_budget_str = str(org_profile.get("budget", "0")).replace(',', '').replace('$', '')
        grant_amount_str = str(grant.get("amount", "")).replace(',', '')
        
        try:
            org_budget_match = re.search(r'\d+', org_budget_str)
            org_budget = float(org_budget_match.group()) if org_budget_match else 0.0
            
            # Extract all numbers from the grant amount string
            grant_numbers = [float(n) for n in re.findall(r'\d+', grant_amount_str)]
            
            if grant_numbers:
                grant_max = max(grant_numbers)
                if org_budget < grant_max:
                    budget_score = 20
                elif org_budget <= 2 * grant_max:
                    budget_score = 15
                else:
                    budget_score = 10
        except Exception:
            pass  # Keep default 15 if parsing fails
            
        # -------------------------------------------------------------
        # d) Focus Area Match (0-30 points)
        # -------------------------------------------------------------
        grant_focus_list = grant.get("focus_areas", [])
        if isinstance(grant_focus_list, str):
            grant_focus_list = [grant_focus_list]
        grant_focus_str = " ".join(grant_focus_list).lower()
        
        area_matches = 0
        partial_match = False
        
        # Split org focus areas by comma for chunk matching
        org_areas = [a.strip().lower() for a in org_focus_str.split(',') if a.strip()]
        
        for area in org_areas:
            if area in grant_focus_str:
                area_matches += 1
            else:
                # Check for partial word match
                words = area.split()
                if any(w in grant_focus_str for w in words if len(w) > 3):
                    partial_match = True
                    
        if area_matches >= 2:
            focus_score = 30
        elif area_matches == 1:
            focus_score = 20
        elif partial_match:
            focus_score = 10
        else:
            focus_score = 0
            
        # Calculate Total
        total = mission_score + location_score + budget_score + focus_score
        
        return {
            "total_score": total,
            "mission_alignment": mission_score,
            "location_match": location_score,
            "budget_fit": budget_score,
            "focus_area_match": focus_score
        }

    async def generate_score_reasoning(self, org_profile: dict, grant: dict, base_scores: dict) -> str:
        """
        Calls Gemini to explain the calculated score in a human-readable way.
        """
        org_name = org_profile.get("name", "Unknown Organization")
        grant_title = grant.get("title", "Unknown Grant")
        grant_funder = grant.get("funder", "Unknown Funder")
        
        prompt = (
            f"Given this eligibility score breakdown for a grant application:\n\n"
            f"Organization: {org_name}\n"
            f"Grant: {grant_title} by {grant_funder}\n\n"
            f"Score Breakdown:\n"
            f"- Mission Alignment: {base_scores.get('mission_alignment')}/30\n"
            f"- Location Match: {base_scores.get('location_match')}/20\n"
            f"- Budget Fit: {base_scores.get('budget_fit')}/20\n"
            f"- Focus Area Match: {base_scores.get('focus_area_match')}/30\n"
            f"- Total Score: {base_scores.get('total_score')}/100\n\n"
            f"Write a 2-3 sentence explanation of this score that tells the "
            f"nonprofit exactly why they scored this way and what they can do "
            f"to strengthen their application. Be specific and actionable.\n"
            f"Return only the explanation text, no labels or headers."
        )
        
        try:
            response = await self.agent.send_message(prompt)
            if response:
                return response.strip()
        except Exception as exc:
            print(f"[EligibilityScorer] Error generating reasoning: {exc}")
            
        return f"Score: {base_scores.get('total_score')}/100 based on mission alignment, location, budget fit, and focus area match."

    async def score_grant(self, org_profile: dict, grant: dict) -> dict:
        """
        Combines base scoring and AI reasoning for a single grant.
        """
        base_scores = self.calculate_base_score(org_profile, grant)
        reasoning = await self.generate_score_reasoning(org_profile, grant, base_scores)
        
        total_score = base_scores["total_score"]
        if total_score >= 70:
            recommendation = "Strong Match"
        elif total_score >= 50:
            recommendation = "Good Match"
        else:
            recommendation = "Weak Match"
            
        return {
            "grant_id": grant.get("id", ""),
            "grant_title": grant.get("title", ""),
            "total_score": total_score,
            "breakdown": base_scores,
            "reasoning": reasoning,
            "recommendation": recommendation
        }

    async def score_all_grants(self, org_profile: dict, grants: list) -> list:
        """
        Scores a list of grants and sorts them by total score descending.
        """
        scored_grants = []
        for grant in grants:
            scored = await self.score_grant(org_profile, grant)
            scored_grants.append(scored)
            
        # Sort descending by total_score
        scored_grants.sort(key=lambda x: x["total_score"], reverse=True)
        return scored_grants


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
scorer = EligibilityScorer()
