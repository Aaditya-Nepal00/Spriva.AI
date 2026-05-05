# Spriva AI

> **Heads up:** We're currently building this project out for the Google Cloud Rapid Agent Hackathon, so it's still very much a work in progress! Expect rough edges while we piece things together.

Spriva helps nonprofits find grant funding they're actually eligible for,
draft the applications, and follow up with funders without the 
bureaucratic nightmare that usually comes with it.

Built using Gemini 2.0 Flash, FastAPI, and Google's MCP servers (Gmail, Calendar, Drive).

---

## What it does

You give Spriva your org's name, mission, and focus areas. It searches 
for matching grants, scores your eligibility against each one, drafts 
full application sections, books deadlines on your calendar, and sends 
intro emails to program officers. All from a single prompt.

- Grant discovery via Gemini web grounding
- Eligibility scoring (0–100) against your org profile
- Full application drafting (executive summary, budget narrative, etc.)
- Deadline tracking via Google Calendar MCP
- Funder outreach via Gmail MCP
- Application storage via Google Drive MCP

---

## Stack

- **AI** — Gemini 2.0 Flash
- **Backend** — FastAPI / Python 3.11
- **Frontend** — React + Vite
- **Actions** — Gmail, Google Calendar, Google Drive (all via MCP)

---

## Setup

```bash
git clone https://github.com/Aaditya-Nepal00/Spriva.AI.git
cd Spriva.AI

cp .env.example .env
# Add your GEMINI_API_KEY to .env

pip install -r requirements.txt
uvicorn backend.main:app --reload --port 5000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

You'll need a `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com).
Google OAuth credentials are required for Calendar, Gmail, and Drive features.

---

## Project layout
backend/
agent/     → Gemini agent loop, tools, prompts
mcp/       → Gmail, Calendar, Drive integrations
grants/    → Search and eligibility scoring
main.py    → FastAPI app
frontend/
src/components/  → React UI

---

## Docker

```bash
docker build -t spriva-ai .
docker run -p 5000:5000 --env-file .env spriva-ai
```

---

MIT License
