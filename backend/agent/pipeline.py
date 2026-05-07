from backend.agent.core import agent
from backend.agent.intake import intake_agent
from backend.elastic.search import elastic_search
from backend.grants.scorer import scorer
from backend.agent.reasoning import reasoning_engine
import json
import re

class SprivaPipeline:
    def __init__(self):
        self.agent = agent
        self.intake = intake_agent
        self.elastic = elastic_search
        self.scorer = scorer
        self.reasoning = reasoning_engine

    async def run_full_pipeline(self, document_text: str, filename: str = "document") -> dict:
        """
        The main feature loop for Spriva AI.
        PDF upload -> org profile extraction -> grant matching -> personalized email drafting.
        """
        try:
            # Step 1 — Extract org profile from document
            intake_result = await self.intake.process_uploaded_text(document_text, filename)
            if intake_result.get("status") == "error":
                return {"status": "error", "step": "document_analysis", "message": intake_result.get("error_message")}
            
            org_profile = {
                "name": intake_result.get("org_name", ""),
                "mission": intake_result.get("mission", ""),
                "focus_areas": intake_result.get("focus_areas", ""),
                "location": intake_result.get("location", ""),
                "budget": intake_result.get("budget_range", ""),
                "programs": intake_result.get("key_programs", ""),
                "past_grants": intake_result.get("past_grants_won", ""),
                "impact_metrics": intake_result.get("impact_metrics", "")
            }

            # Step 2 — Search for matching grants
            grants = self.elastic.search_grants(org_profile)
            if not grants:
                return {"status": "error", "step": "grant_search", "message": "No matching grants found for this organization profile."}

            # Step 3 — Score and rank grants
            ranked_scores = await self.reasoning.quick_rank(org_profile, grants)
            if not ranked_scores:
                return {"status": "error", "step": "grant_ranking", "message": "Failed to score and rank grants."}
            
            # Take the top ranked grant as best_grant
            top_score = ranked_scores[0]
            best_grant = next((g for g in grants if g.get("id") == top_score.get("grant_id")), None)
            
            if not best_grant:
                return {"status": "error", "step": "grant_ranking", "message": "Could not identify the top grant details."}

            # Step 4 — Build funder profile from best grant
            funder_name = best_grant.get("funder", "Unknown Funder")
            funder_website = best_grant.get("funder_website", "")
            funder_email = best_grant.get("funder_email", "")
            funder_twitter = best_grant.get("funder_twitter", "")
            funder_linkedin = best_grant.get("funder_linkedin", "")
            program_officer = best_grant.get("program_officer", "Program Officer")
            funder_description = best_grant.get("funder_description", "")
            grant_title = best_grant.get("title", "Grant Program")
            amount = best_grant.get("amount_text", "")
            deadline = best_grant.get("deadline", "")

            # Step 5 — Draft personalized outreach email
            prompt = f"""You are writing a grant funding outreach email on behalf of {org_profile['name']}.
        
Organization Background (from their documents):
Mission: {org_profile['mission']}
Focus Areas: {org_profile['focus_areas']}
Location: {org_profile['location']}
Key Programs: {org_profile['programs']}
Past Grants: {org_profile['past_grants']}
Impact Metrics: {org_profile['impact_metrics']}

Funder Details:
Funder: {funder_name}
Grant Program: {grant_title}
Amount Available: {amount}
Program Officer: {program_officer}
Funder Focus: {funder_description}

Write a professional, warm outreach email that:
1. Opens with a specific connection to the funder's stated priorities
2. Briefly introduces the org using their ACTUAL programs and impact numbers from the documents
3. Explains why this specific grant is a strong fit
4. Closes with a clear ask for a conversation
5. Is between 200-250 words — not too long
6. Sounds like a real person wrote it, not AI

Return ONLY a JSON object with keys:
- subject: email subject line
- body: full email body
- to_email: {funder_email}
- to_name: {program_officer}
- personalization_notes: list of 2-3 specific things from the org's documents that were used to personalize this email"""

            response = await self.agent.send_message(prompt)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                return {"status": "error", "step": "email_drafting", "message": "Failed to parse email draft JSON."}
            
            email_data = json.loads(match.group())

            # Step 6 — Return complete result
            return {
                "status": "complete",
                "org_profile": org_profile,
                "additional_info": {
                    "source_file": filename,
                    "budget_range": intake_result.get("budget_range"),
                    "past_grants_won": intake_result.get("past_grants_won")
                },
                "best_grant": best_grant,
                "all_grants": ranked_scores,
                "email_draft": {
                    "subject": email_data.get("subject"),
                    "body": email_data.get("body"),
                    "to_email": funder_email,
                    "to_name": program_officer,
                    "funder_website": funder_website,
                    "funder_twitter": funder_twitter,
                    "funder_linkedin": funder_linkedin,
                    "personalization_notes": email_data.get("personalization_notes"),
                    "status": "pending_approval"
                },
                "pipeline_steps": [
                    "document_analyzed",
                    "grants_searched", 
                    "grants_ranked",
                    "email_drafted"
                ]
            }

        except Exception as e:
            return {
                "status": "error", 
                "step": "pipeline_execution", 
                "message": str(e)
            }

    async def get_best_grant_only(self, org_profile: dict) -> dict:
        """
        Simpler version — no document intake.
        Takes org_profile directly and runs steps 2-5 only.
        """
        try:
            # Re-map org_profile keys if necessary to match the prompt context
            org_name = org_profile.get("name", org_profile.get("org_name", "Organization"))
            mission = org_profile.get("mission", "")
            focus_areas = org_profile.get("focus_areas", "")
            location = org_profile.get("location", "")
            programs = org_profile.get("programs", org_profile.get("key_programs", "N/A"))
            past_grants = org_profile.get("past_grants", org_profile.get("past_grants_won", "N/A"))
            metrics = org_profile.get("impact_metrics", "N/A")

            # Step 2 — Search for matching grants
            grants = self.elastic.search_grants(org_profile)
            if not grants:
                return {"status": "error", "step": "grant_search", "message": "No matching grants found for this profile."}

            # Step 3 — Score and rank grants
            ranked_scores = await self.reasoning.quick_rank(org_profile, grants)
            if not ranked_scores:
                return {"status": "error", "step": "grant_ranking", "message": "Failed to score and rank grants."}
            
            top_score = ranked_scores[0]
            best_grant = next((g for g in grants if g.get("id") == top_score.get("grant_id")), None)
            
            if not best_grant:
                return {"status": "error", "step": "grant_ranking", "message": "Could not identify the top grant details."}

            # Step 4 — Build funder profile from best grant
            funder_name = best_grant.get("funder", "Unknown Funder")
            funder_website = best_grant.get("funder_website", "")
            funder_email = best_grant.get("funder_email", "")
            funder_twitter = best_grant.get("funder_twitter", "")
            funder_linkedin = best_grant.get("funder_linkedin", "")
            program_officer = best_grant.get("program_officer", "Program Officer")
            funder_description = best_grant.get("funder_description", "")
            grant_title = best_grant.get("title", "Grant Program")
            amount = best_grant.get("amount_text", "")

            # Step 5 — Draft personalized outreach email
            prompt = f"""You are writing a grant funding outreach email on behalf of {org_name}.
        
Organization Background:
Mission: {mission}
Focus Areas: {focus_areas}
Location: {location}
Key Programs: {programs}
Past Grants: {past_grants}
Impact Metrics: {metrics}

Funder Details:
Funder: {funder_name}
Grant Program: {grant_title}
Amount Available: {amount}
Program Officer: {program_officer}
Funder Focus: {funder_description}

Write a professional, warm outreach email that:
1. Opens with a specific connection to the funder's stated priorities
2. Briefly introduces the org using their ACTUAL programs and impact numbers
3. Explains why this specific grant is a strong fit
4. Closes with a clear ask for a conversation
5. Is between 200-250 words — not too long
6. Sounds like a real person wrote it, not AI

Return ONLY a JSON object with keys:
- subject: email subject line
- body: full email body
- to_email: {funder_email}
- to_name: {program_officer}
- personalization_notes: list of 2-3 specific things used to personalize this email"""

            response = await self.agent.send_message(prompt)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                return {"status": "error", "step": "email_drafting", "message": "Failed to parse email draft JSON."}
            
            email_data = json.loads(match.group())

            return {
                "status": "complete",
                "org_profile": org_profile,
                "best_grant": best_grant,
                "all_grants": ranked_scores,
                "email_draft": {
                    "subject": email_data.get("subject"),
                    "body": email_data.get("body"),
                    "to_email": funder_email,
                    "to_name": program_officer,
                    "funder_website": funder_website,
                    "funder_twitter": funder_twitter,
                    "funder_linkedin": funder_linkedin,
                    "personalization_notes": email_data.get("personalization_notes"),
                    "status": "pending_approval"
                },
                "pipeline_steps": [
                    "grants_searched", 
                    "grants_ranked",
                    "email_drafted"
                ]
            }
        except Exception as e:
            return {"status": "error", "step": "pipeline_execution", "message": str(e)}

pipeline = SprivaPipeline()
