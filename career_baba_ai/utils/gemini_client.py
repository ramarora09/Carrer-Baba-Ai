import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

try:
    from career_baba_ai.utils.local_ml_engine import generate_local_career_intelligence
except ModuleNotFoundError:
    from utils.local_ml_engine import generate_local_career_intelligence


DEFAULT_MODEL = "gemini-2.5-flash-lite"


def _get_api_key():
    return os.getenv("GEMINI_API_KEY", "").strip().strip("\"'")


def gemini_configured():
    api_key = _get_api_key()
    return bool(api_key and api_key != "your_gemini_api_key_here")


def _extract_json(text):
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def fallback_profile(payload, key_configured=False):
    return generate_local_career_intelligence(payload)


def gemini_enhancement_enabled():
    return os.getenv("ENABLE_GEMINI_ENHANCEMENT", "").lower() == "true"


def generate_career_intelligence(payload):
    api_key = _get_api_key()
    fallback = generate_local_career_intelligence(payload)
    if not gemini_enhancement_enabled():
        return fallback, False, "Using local AI/ML engine: skill extraction, vector role matching, gap scoring, and roadmap generation."

    if not gemini_configured():
        return fallback, False, "Local AI/ML engine used. Gemini enhancement is enabled, but GEMINI_API_KEY is not configured."

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    encoded_model = urllib.parse.quote(model, safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{encoded_model}:generateContent"

    prompt = f"""
You are Career Baba AI, an AI/ML career intelligence engine.

Use the user's profile and resume text to dynamically infer:
- skills
- best-fit career roles
- current market demand for top roles
- skill gaps
- matched and missing skills
- role readiness
- why the suggested role fits
- required role skills
- companies or employer categories to target
- skill recommendations
- learning roadmap
- portfolio projects
- resume feedback
- market guidance

Do not rely on static datasets. Infer from the user's inputs and current general technology hiring patterns.
Be practical for students, freshers, and early-career professionals.

User payload:
{json.dumps(payload, indent=2)}

Local model prediction:
{json.dumps(fallback, indent=2)}

Return only valid JSON with exactly this shape:
{{
  "profile_summary": "string",
  "detected_skills": ["string"],
  "market_demand": [
    {{
      "role": "string",
      "demand_score": 0,
      "trend": "string"
    }}
  ],
  "top_roles": [
    {{
      "title": "string",
      "fit_score": 0,
      "why": "string",
      "growth_signal": "string"
    }}
  ],
  "selected_role": "string",
  "why_this_role": ["string"],
  "required_skills": ["string"],
  "target_companies": ["string"],
  "skill_gap": {{
    "strong_skills": ["string"],
    "missing_skills": ["string"],
    "readiness_score": 0
  }},
  "skill_match": {{
    "matched": ["string"],
    "missing": ["string"]
  }},
  "recommended_skills": ["string"],
  "top_career_options": [
    {{
      "title": "string",
      "fit_score": 0
    }}
  ],
  "learning_plan": [
    {{
      "phase": "string",
      "duration": "string",
      "actions": "string"
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "level": "Beginner|Intermediate|Advanced",
      "description": "string",
      "success_metrics": ["string"]
    }}
  ],
  "resume_feedback": ["string"],
  "market_insights": ["string"],
  "next_actions": ["string"]
}}
"""

    body = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Return strict JSON only. Be specific, modern, practical, and concise. "
                        "Avoid generic motivation."
                    )
                }
            ]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }

    if os.getenv("ENABLE_GEMINI_SEARCH", "").lower() == "true":
        body["tools"] = [{"google_search": {}}]

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        return fallback, False, _format_gemini_error(exc.code, detail)
    except urllib.error.URLError as exc:
        return fallback, False, f"Gemini request failed. Showing fallback guidance. {exc.reason}"

    text = "".join(
        part.get("text", "")
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    )
    parsed = _extract_json(text)
    if not parsed:
        candidate = data.get("candidates", [{}])[0]
        finish_reason = candidate.get("finishReason")
        reason = f" Finish reason: {finish_reason}." if finish_reason else ""
        return fallback, False, f"Gemini returned an invalid or incomplete JSON response.{reason} Showing fallback guidance."

    parsed["engine"] = "local_ml_with_gemini_enhancement"

    grounding_chunks = (
        data.get("candidates", [{}])[0]
        .get("groundingMetadata", {})
        .get("groundingChunks", [])
    )
    sources = []
    for chunk in grounding_chunks:
        web = chunk.get("web", {})
        if web.get("uri"):
            sources.append({"title": web.get("title") or web["uri"], "url": web["uri"]})

    if sources:
        parsed["sources"] = sources[:6]

    return parsed, True, "Local AI/ML prediction enhanced by Gemini language generation."


def _format_gemini_error(status_code, detail):
    message = "Gemini request failed. Showing fallback guidance."
    parsed = _extract_json(detail)
    api_message = ""
    if isinstance(parsed, dict):
        api_message = parsed.get("error", {}).get("message", "")

    if status_code in (400, 401, 403) and "API key" in api_message:
        return f"{message} Check GEMINI_API_KEY in your .env file. Gemini says: {api_message}"

    if status_code == 404:
        return f"{message} Check GEMINI_MODEL in your .env file. Gemini says: {api_message or detail}"

    if status_code == 429:
        return f"{message} Gemini quota or rate limit was reached. Gemini says: {api_message or detail}"

    return f"{message} Gemini says: {api_message or detail}"
