# Spriva AI

AI agent that helps nonprofits find funding they actually qualify 
for, draft the applications, and follow up with funders.

Built for the Google Cloud Rapid Agent Hackathon using Gemini 2.5 
Flash, Elasticsearch, and Google MCP servers.

---

## The problem

Small nonprofits miss billions in available funding every year. Not 
because they don't qualify — because they don't have the time or 
resources to find, apply, and follow up properly. Spriva fixes that.

---

## How it works

You give Spriva your org name, mission, and focus areas. It searches 
an Elasticsearch index of grant opportunities, scores your 
eligibility with reasoning, drafts the full application, books 
deadlines on your calendar, and emails the funder. All from one 
prompt.

---

## Features

- Grant discovery via Elasticsearch semantic search
- Eligibility scoring with transparent reasoning
- Full application drafting powered by Gemini 2.5 Flash
- Deadline tracking via Google Calendar MCP
- Funder outreach + 7-day follow-up via Gmail MCP
- Application storage via Google Drive MCP
- Document Intake — upload past grant PDFs, Spriva builds
  your org profile automatically

---

## Stack

- **AI** — Gemini 2.5 Flash
- **Search** — Elasticsearch (Elastic Cloud Serverless)
- **Backend** — FastAPI / Python 3.11
- **Frontend** — React + Vite
- **Actions** — Gmail, Google Calendar, Google Drive

---

## Setup

```bash
git clone https://github.com/Aaditya-Nepal00/Spriva.AI.git
cd Spriva.AI
cp .env.example .env
# Add your API keys to .env
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 5000
```

Requires:
- `GEMINI_API_KEY` from [Google Cloud Console](https://console.cloud.google.com)
- `ELASTIC_ENDPOINT` and `ELASTIC_API_KEY` from [elastic.co/cloud](https://elastic.co/cloud)
- Google OAuth credentials for Calendar, Gmail, Drive

---

## Project layout
backend/
agent/    → Gemini brain, tools, prompts
elastic/  → Elasticsearch grant search
mcp/      → Gmail, Calendar, Drive integrations
grants/   → Eligibility scoring
main.py   → FastAPI app
frontend/
src/components/  → React UI

---

MIT License