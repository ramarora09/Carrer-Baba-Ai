# Career Baba AI

Career Baba AI is a Python AI/ML-style web application with a professional custom UI and a local career intelligence engine.

The core recommendation flow no longer depends on Gemini. It uses local skill extraction, TF-IDF-style role vector matching, readiness scoring, skill-gap analysis, and dynamic roadmap/project generation from the user's profile and resume text. Gemini can still be enabled as an optional language enhancement layer.

## Features

- Professional web UI served by FastAPI
- Local skill extraction from profile and resume text
- TF-IDF-style role vector matching
- Local readiness and skill-gap scoring
- Dynamic learning roadmap generation
- Dynamic portfolio project recommendations
- Resume feedback from local profile signals
- Market demand scoring from role profiles and skill overlap
- Optional Gemini enhancement for rewritten report language
- Optional Gemini Google Search grounding for fresher market information
- PDF resume upload or resume text paste
- Works without a Gemini API key

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

## Optional Gemini Enhancement

The app works without Gemini. To let Gemini rewrite or enrich the local model's output, edit the root `.env` file:

```bash
GEMINI_API_KEY=paste_your_real_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
ENABLE_GEMINI_ENHANCEMENT=true
ENABLE_GEMINI_SEARCH=false
```

The file to change is:

```text
Career-Baba-Ai/.env
```

Do not change `.env.example`; it is only a template.

Get a Gemini key:

```text
https://aistudio.google.com/app/apikey
```

Recommended default:

```bash
GEMINI_MODEL=gemini-2.5-flash-lite
```

Optional live web grounding:

```bash
ENABLE_GEMINI_SEARCH=true
```

Keep Gemini enhancement and search grounding off for a fully local AI/ML-style project. Turn them on only when you want hosted LLM language enhancement or fresher sourced market insights.

## Project Structure

```text
career_baba_ai/
  app.py                  # FastAPI web app and API routes
  templates/
    auth.html
    index.html            # Professional UI
  static/
    styles.css
    app.js
  utils/
    local_ml_engine.py    # Local AI/ML-style skill extraction, role ranking, and scoring
    gemini_client.py      # Optional Gemini enhancement wrapper
    resume_parser.py      # PDF text extraction
```

## Deployment

This is no longer a Next.js project. Deploy it as a Python web app on:

- Render
- Railway
- Fly.io
- Google Cloud Run
- Azure App Service

Typical start command:

```bash
uvicorn career_baba_ai.app:app --host 0.0.0.0 --port $PORT
```

## Notes

- The local engine is the main intelligence layer.
- Gemini is optional, not required.
- The role profiles are currently embedded in Python. For a stronger ML project, move them into a dataset and add evaluation/training notebooks.
