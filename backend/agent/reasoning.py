"""
backend/agent/reasoning.py
--------------------------
The automated reasoning layer for Spriva AI.
Takes raw ElasticSearch results, scores them, and uses Gemini to reason over them 
to pick the best matches for the organization.
"""

from backend.agent.core import agent
from backend.grants.scorer import scorer
import json
import re

class GrantReasoningEngine:
    def __init__(self):
        self.agent = agent
        self.scorer = scorer

    async def reason_over_grants(self, org_profile: dict, grants: list) -> dict:
        """
        The core reasoning loop. Scores all grants, takes the top 3, and asks Gemini
        to act as an expert advisor to rank and recommend the best fit.
        """
        try:
            if not grants:
                return {"status": "error", "error_message": "No grants provided for reasoning."}
            
            # Step 1: Score all grants
            scored_grants = await self.scorer.score_all_grants(org_profile, grants)
            
            # Step 2: Take top 3 scored grants
            top_3_scores = scored_grants[:3]
            top_3_ids = [s["grant_id"] for s in top_3_scores]
            top_3_grants = [g for g in grants if g.get("id") in top_3_ids]
            
            # Build score summary for the prompt
            score_summary = [
                {
                    "grant_id": s["grant_id"], 
                    "title": s["grant_title"], 
                    "total_score": s["total_score"],
                    "reasoning": s["reasoning"]
                }
                for s in top_3_scores
            ]
            
            org_name = org_profile.get('name', 'Unknown')
            org_mission = org_profile.get('mission', 'Unknown')
            org_focus_areas = org_profile.get('focus_areas', 'Unknown')
            org_location = org_profile.get('location', 'Unknown')
            org_budget = org_profile.get('budget', 'Unknown')
            
            # Step 3: Build the reasoning prompt
            prompt = f"""You are an expert grant advisor. An NGO has the following profile:

Name: {org_name}
Mission: {org_mission}
Focus Areas: {org_focus_areas}
Location: {org_location}
Annual Budget: {org_budget}

Elasticsearch found these matching grants:
{json.dumps(top_3_grants, indent=2)}

Their eligibility scores are:
{json.dumps(score_summary, indent=2)}

As an expert advisor, analyze these grants and provide:
1. The BEST fit grant and exactly why it suits this org
2. Any red flags or concerns for each grant
3. Which grant has the highest chance of success
4. One specific thing this org should emphasize in each application

Return ONLY a JSON object with these exact keys:
- best_fit_grant_id: string
- best_fit_reason: string (2-3 sentences)
- ranked_grants: list of objects, each with:
    grant_id, title, rank, confidence_score (0-100),
    why_good_fit, red_flags, emphasis_tip
- overall_recommendation: string (1 paragraph)
- estimated_success_rate: string like 'High/Medium/Low'

Return only JSON, no other text."""

            # Step 4: Parse Gemini response
            response = await self.agent.send_message(prompt)
            
            # Extract JSON block even if wrapped in markdown
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No valid JSON found in Gemini response")
                
            parsed_reasoning = json.loads(match.group())
            
            best_fit_id = parsed_reasoning.get("best_fit_grant_id")
            best_fit_grant_title = next((g.get("title") for g in top_3_grants if g.get("id") == best_fit_id), "Unknown Grant")
            
            # Step 5: Combine everything into final output
            return {
                "org_name": org_name,
                "grants_found": len(grants),
                "grants_analyzed": len(top_3_grants),
                "best_fit": best_fit_grant_title,
                "reasoning": parsed_reasoning,
                "scored_grants": scored_grants,
                "status": "complete"
            }
            
        except Exception as e:
            print(f"Error in reasoning engine: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }

    async def quick_rank(self, org_profile: dict, grants: list) -> list:
        """
        Faster version — no Gemini call, just scorer ranking.
        Scores all grants, sorts by total_score descending, and adds a rank field.
        """
        try:
            scored_grants = await self.scorer.score_all_grants(org_profile, grants)
            
            # Add rank field
            for index, scored in enumerate(scored_grants):
                scored["rank"] = index + 1
                
            return scored_grants
        except Exception as e:
            print(f"Error in quick_rank: {e}")
            return []

    async def get_best_grant(self, org_profile: dict, grants: list) -> dict:
        """
        Returns only the single best grant with full reasoning attached.
        """
        try:
            reasoning_result = await self.reason_over_grants(org_profile, grants)
            
            if reasoning_result.get("status") == "error":
                return reasoning_result
                
            parsed_reasoning = reasoning_result.get("reasoning", {})
            best_fit_id = parsed_reasoning.get("best_fit_grant_id")
            
            best_grant = next((g for g in grants if g.get("id") == best_fit_id), None)
            
            if not best_grant:
                # Fallback to the top scored grant if id matching fails
                scored_grants = reasoning_result.get("scored_grants", [])
                if scored_grants:
                    best_fit_id = scored_grants[0].get("grant_id")
                    best_grant = next((g for g in grants if g.get("id") == best_fit_id), None)
            
            return {
                "grant": best_grant,
                "best_fit_reason": parsed_reasoning.get("best_fit_reason"),
                "overall_recommendation": parsed_reasoning.get("overall_recommendation"),
                "estimated_success_rate": parsed_reasoning.get("estimated_success_rate"),
                "status": "complete"
            }
            
        except Exception as e:
            print(f"Error getting best grant: {e}")
            return {"status": "error", "error_message": str(e)}

# Create instance at bottom
reasoning_engine = GrantReasoningEngine()
