# Career Baba AI

Career Baba AI is now a Python AI/ML-style web application with a professional custom UI and Gemini-powered career intelligence.

It no longer uses CSV datasets or hard-coded role data. User-facing features are generated dynamically from the user's profile, resume text, and Gemini model output.

## Features

- Professional web UI served by FastAPI
- Gemini-powered skill extraction
- Dynamic role matching
- AI-generated skill gap analysis
- AI-generated learning roadmap
- AI-generated portfolio project ideas
- AI-generated resume feedback
- AI-generated market insights
- Optional Gemini Google Search grounding for fresher market information
- PDF resume upload or resume text paste
- Local fallback report if no Gemini key is configured

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

Edit the root `.env` file before running:

```bash
GEMINI_API_KEY=paste_your_real_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
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

Keep search grounding off for cheaper/free long use. Turn it on when you want fresher market insights and source links.

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
    gemini_client.py      # Gemini model calls and fallback
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

- CSV datasets were removed.
- Static role maps and rule-based recommendation files were removed.
- Gemini is the intelligence layer now.
- The fallback report exists only so the UI still works without an API key.
