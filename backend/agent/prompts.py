"""
backend/agent/prompts.py
------------------------
Contains all system prompts and prompt templates for the Gemini agent.
Abstracts the prompt engineering out of the core logic files.
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# 1. Used to initialize the SprivaAgent's persona and constraints
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are Spriva, an expert AI grant funding assistant for nonprofits 
and NGOs. You help organizations find grants they are eligible for, 
score eligibility with clear reasoning, draft professional grant 
applications, track deadlines, and coordinate funder outreach.

Always be specific, practical, and results-focused.
When returning JSON, return only valid JSON with no extra text.
Never hallucinate grant information — only suggest real programs.
Always explain your scoring reasoning transparently."""


# ---------------------------------------------------------------------------
# 2. Used in backend/grants/search.py to discover tailored grant opportunities
# ---------------------------------------------------------------------------
def grant_search_prompt(org_profile: dict) -> str:
    name = org_profile.get("name", "")
    mission = org_profile.get("mission", "")
    focus_areas = org_profile.get("focus_areas", "")
    location = org_profile.get("location", "")
    budget = org_profile.get("budget", "")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""You are a grant research expert. Find 6 real, currently active 
grant opportunities for this nonprofit organization.

Organization: {name}
Mission: {mission}
Focus Areas: {focus_areas}
Location: {location}
Annual Budget: {budget}
Current Date: {current_date}

Search your knowledge for real grants from foundations, government agencies, 
and corporations that match this org.

Return ONLY a valid JSON array. Each grant object must have exactly these fields:
- id: unique string like 'grant_001'
- title: full grant program name
- funder: organization giving the grant
- funder_type: one of [Foundation, Government, Corporate, UN Agency]
- amount: funding range as string e.g. 'Up to $50,000'
- deadline: next deadline as string
- focus_areas: list of strings
- location_requirement: string
- description: 2-3 sentence description
- application_url: URL string
- requirements: list of 3-4 key requirements

Return ONLY the JSON array. No explanation. No markdown."""


# ---------------------------------------------------------------------------
# 3. Used in backend/agent/core.py to generate full application drafts
# ---------------------------------------------------------------------------
def application_draft_prompt(org_profile: dict, grant: dict) -> str:
    org_name = org_profile.get("name", "")
    org_mission = org_profile.get("mission", "")
    grant_title = grant.get("title", "")
    grant_funder = grant.get("funder", "")
    grant_amount = grant.get("amount", "")
    
    return f"""Draft a complete grant application for:
Organization: {org_name}
Mission: {org_mission}
Grant: {grant_title} by {grant_funder}
Grant Amount: {grant_amount}

Return ONLY a JSON object with these exact keys:
- executive_summary (2 paragraphs)
- organization_background (2 paragraphs)
- project_description (3 paragraphs)
- goals_and_objectives (list of 4 specific goals)
- budget_narrative (1 paragraph)
- evaluation_plan (1 paragraph)
- conclusion (1 paragraph)

Return only the JSON object, no other text."""


# ---------------------------------------------------------------------------
# 4. Used in backend/grants/scorer.py to generate human-readable reasoning
# ---------------------------------------------------------------------------
def score_reasoning_prompt(org_profile: dict, grant: dict, scores: dict) -> str:
    org_name = org_profile.get("name", "")
    grant_title = grant.get("title", "")
    grant_funder = grant.get("funder", "")
    
    return f"""Given this eligibility score breakdown for a grant application:

Organization: {org_name}
Grant: {grant_title} by {grant_funder}

Score Breakdown:
- Mission Alignment: {scores.get('mission_alignment')}/30
- Location Match: {scores.get('location_match')}/20  
- Budget Fit: {scores.get('budget_fit')}/20
- Focus Area Match: {scores.get('focus_area_match')}/30
- Total Score: {scores.get('total_score')}/100

Write a 2-3 sentence explanation of this score that tells the 
nonprofit exactly why they scored this way and what they can do 
to strengthen their application. Be specific and actionable.
Must include:
- What matched well
- What didn't match
- One specific actionable tip to improve the application

Return only the explanation text, no labels or headers."""


# ---------------------------------------------------------------------------
# 5. Used by the Gmail MCP tool to assist with funder communications
# ---------------------------------------------------------------------------
def followup_email_prompt(org_name: str, grant_title: str, funder_name: str, days_since_first: int) -> str:
    return f"""Draft a polite follow-up email for a nonprofit that sent an initial outreach email {days_since_first} days ago and has not received a reply.

Context:
From Organization: {org_name}
Regarding Grant: {grant_title}
To Funder: {funder_name}

The email should be brief, professional, and non-pushy. Return ONLY the email text."""


# ---------------------------------------------------------------------------
# 6. Used by the document processing flow to automatically build org profiles
# ---------------------------------------------------------------------------
def document_intake_prompt(document_text: str) -> str:
    return f"""Extract the core organization profile information from the following grant application PDF or annual report text.

Document Text:
{document_text}

Extract the following information and return ONLY a JSON object with these exact keys:
- org_name (string)
- mission (string)
- focus_areas (string, comma separated)
- location (string)
- budget_range (string)
- past_grants_won (list of strings)
- key_programs (list of strings)
- impact_metrics (list of strings)

Return only the JSON object, no other text."""
