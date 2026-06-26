# Career Baba AI

Career Baba AI is a RAG-powered LLM career guidance platform built with FastAPI, Gemini, and a custom AI/ML career scoring layer. It helps students, freshers, and early-career professionals get personalized career direction from their profile or resume.

The project is not just a Gemini API wrapper. It combines:

- A career knowledge base
- TF-IDF vector retrieval for RAG grounding
- Resume/profile skill extraction
- Role matching and readiness scoring
- Gemini-powered final answer generation
- A professional web UI with report generation and career chat

## Features

- RAG-powered AI career chatbot
- AI Career Intelligence Report
- PDF resume upload or resume text paste
- Profile-based role recommendation
- Skill-gap and readiness scoring
- Market demand guidance
- Personalized learning roadmap
- Portfolio project recommendations
- Resume feedback
- Internal RAG source tracking
- Works with Gemini for polished LLM responses
- Falls back to knowledge-grounded guidance if Gemini is unavailable

## Architecture

```text
User profile / resume / chat question
        ↓
Profile and resume signal analysis
        ↓
Career knowledge base retrieval
        ↓
RAG context + profile analysis
        ↓
Gemini LLM generation
        ↓
Personalized career report or chatbot reply
```

## Run Locally

```bash
cd Career-Baba-Ai
pip install -r requirements.txt
uvicorn career_baba_ai.app:app --reload
```

Open:

```text
http://localhost:8000
```

## Gemini Setup

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=paste_your_real_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
ENABLE_GEMINI_ENHANCEMENT=true
ENABLE_GEMINI_SEARCH=false
AUTH_SECRET=change_this_to_a_long_random_secret
```

Get a Gemini key:

```text
https://aistudio.google.com/app/apikey
```

## Project Structure

```text
career_baba_ai/
  app.py                    # FastAPI web app and API routes
  knowledge/
    career_knowledge.json   # RAG knowledge base
  templates/
    auth.html
    index.html              # Professional UI
  static/
    styles.css
    app.js
  utils/
    rag_engine.py           # TF-IDF vector retrieval for RAG
    local_ml_engine.py      # Skill extraction, role ranking, scoring
    gemini_client.py        # Gemini + RAG prompt orchestration
    resume_parser.py        # PDF text extraction
```

## Useful API Routes

```text
POST /api/analyze       Generate AI career report
POST /api/resume        Analyze uploaded/pasted resume
POST /api/chat          Ask the RAG career advisor
POST /api/rag/search    Inspect retrieved knowledge chunks
GET  /api/health        Check app, Gemini, and RAG status
```

## Deployment

Deploy as a Python web app:

- Google Cloud Run
- Render paid instance
- Railway
- Fly.io
- Azure App Service

Typical start command:

```bash
uvicorn career_baba_ai.app:app --host 0.0.0.0 --port $PORT
```

For a public product, prefer Google Cloud Run with minimum instances enabled or a paid hosting plan so users do not see cold-start loading screens.
