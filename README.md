# Spriva AI

Grant funding agent for nonprofits.

---

## The problem

Small nonprofits miss billions in available funding every year.
Not because they don't qualify — because they don't have the 
time or people to find, apply, and follow up properly.

Spriva fixes that.

---

## What it does

Give Spriva your org's name, mission, and focus areas or 
drop in a past grant application and let it read the document 
itself. From there it handles everything:

- Searches an Elasticsearch index of grant opportunities using 
  semantic matching on your mission and focus areas
- Runs a live web search for current global grants using 
  Gemini's Google Search tool
- Scores each result across four criteria with transparent 
  reasoning — not just a number, but why
- Picks the best fit and drafts a full application section 
  by section
- Books the deadline on Google Calendar
- Drafts a personalized outreach email to the program officer
- Checks for replies after 7 days and drafts a follow-up
- Saves everything to a structured folder in Google Drive

All of this from one input.

---

## How it works

Document Upload
↓
Gemini reads it → builds org profile
↓
Elasticsearch search + live Google Search
↓
Mathematical scorer + Gemini reasoning
↓
Best grant selected
↓
Application drafted → Gmail → Calendar → Drive

---

## Stack

- **AI** — Gemini 2.5 Flash via Vertex AI
- **Search** — Elasticsearch (Elastic Cloud Serverless)
- **Backend** — FastAPI / Python 3.11
- **Frontend** — React + Vite (dark, responsive)
- **Actions** — Gmail, Calendar, Drive via Google MCP

---

## Setup

```bash
git clone https://github.com/Aaditya-Nepal00/Spriva.AI.git
cd Spriva.AI

cp .env.example .env
# Fill in GEMINI_API_KEY, ELASTIC_ENDPOINT, 
# ELASTIC_API_KEY, GOOGLE_CLOUD_PROJECT

pip install -r requirements.txt
uvicorn backend.main:app --reload --port 5000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Requires a Google Cloud project with Vertex AI enabled and 
an Elastic Cloud Serverless deployment.

---

## Project layout

backend/
agent/    → Gemini brain, reasoning engine, pipelines
elastic/  → Elasticsearch search and indexing
mcp/      → Gmail, Calendar, Drive integrations
grants/   → Eligibility scoring logic
main.py   → FastAPI app
frontend/
src/
pages/      → Dashboard, Intake, Discovery, Drafts, Chat
components/ → Cards, panels, navigation
context/    → Global state

---

MIT License