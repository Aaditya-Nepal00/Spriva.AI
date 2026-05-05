# Spriva AI 🌱

> An AI-powered grant funding assistant for nonprofits and NGOs built for the Google Gemini Hackathon.

Spriva AI helps nonprofits find grant funding opportunities, score their eligibility, draft full grant applications, track deadlines, and send funder outreach emails — all powered by **Gemini 2.0 Flash**.

---

## ✨ Features

- 🔍 **Grant Discovery** — Searches the web for relevant grant opportunities based on your org's mission and focus areas
- 📊 **Eligibility Scoring** — Scores each grant opportunity against your organization's profile
- ✍️ **Application Drafting** — Generates full grant application drafts using Gemini 2.0 Flash
- 📅 **Deadline Tracking** — Adds grant deadlines to Google Calendar via MCP
- 📧 **Funder Outreach** — Drafts and sends outreach emails via Gmail MCP
- 📁 **Drive Integration** — Saves drafted applications to Google Drive via MCP

---

## 🛠 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| AI Brain  | Gemini 2.0 Flash (Google GenAI)     |
| Backend   | FastAPI + Python                    |
| Frontend  | React (Vite)                        |
| MCP Tools | Gmail, Google Calendar, Google Drive|

---

## 📁 Project Structure

```
Spriva.AI/
├── backend/
│   ├── agent/          # Gemini agent loop, tools, prompts
│   ├── mcp/            # Gmail, Calendar, Drive MCP integrations
│   ├── grants/         # Grant search and eligibility scoring
│   ├── main.py         # FastAPI entry point
│   └── config.py       # Environment config
├── frontend/
│   ├── public/
│   └── src/
│       └── components/ # React UI components
├── .env.example
├── requirements.txt
└── Dockerfile
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Aaditya-Nepal00/Spriva.AI.git
cd Spriva.AI
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Required API Keys

| Key                    | Where to Get It                          |
|------------------------|------------------------------------------|
| `GEMINI_API_KEY`       | [Google AI Studio](https://aistudio.google.com/) |
| `GOOGLE_CLIENT_ID`     | [Google Cloud Console](https://console.cloud.google.com/) |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console → OAuth 2.0         |
| `SECRET_KEY`           | Any random secret string                 |

---

## 🐳 Docker

```bash
docker build -t spriva-ai .
docker run -p 8000:8000 --env-file .env spriva-ai
```

---

## 📄 License

MIT — see [LICENSE](./LICENSE)
