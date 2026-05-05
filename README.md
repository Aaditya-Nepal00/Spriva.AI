# Spriva AI

An AI agent that helps nonprofits find grants, check eligibility, 
draft applications, and follow up with funders.

Built for the Google Cloud Rapid Agent Hackathon using Gemini 2.0 
Flash and Google MCP servers.

---

## The problem

Small nonprofits miss billions in available grant funding every year. 
Not because they don't qualify — because they don't have the time or 
resources to find, apply, and follow up properly.

Spriva fixes that.

---

## Features

- Grant discovery powered by Gemini 2.0 Flash
- Eligibility scoring with transparent reasoning
- Full application drafting
- Deadline tracking via Google Calendar MCP
- Funder outreach and follow-ups via Gmail MCP
- Application storage via Google Drive MCP
- Document Intake — upload past grant PDFs and let Spriva 
  build your org profile automatically

---

## Stack

Gemini 2.0 Flash · FastAPI · React · Google MCP

---

## Setup

```bash
git clone https://github.com/Aaditya-Nepal00/Spriva.AI.git
cd Spriva.AI
cp .env.example .env
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 5000
```

Requires a `GEMINI_API_KEY` from [aistudio.google.com](https://aistudio.google.com).

---

MIT License
