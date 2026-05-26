import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


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
    skills = payload.get("skills", [])
    if isinstance(skills, str):
        skills = [skill.strip().lower() for skill in skills.split(",") if skill.strip()]

    role = payload.get("target_role") or payload.get("interest") or "Technology Career"
    missing = [
        "portfolio project depth",
        "interview preparation",
        "role-specific proof of work",
        "resume storytelling",
    ]

    return {
        "profile_summary": (
            f"Your profile is being analyzed for {role}. "
            + (
                "Gemini responded, but the app could not use the response, so this fallback report is shown."
                if key_configured
                else "Add a Gemini key for fully dynamic AI results."
            )
        ),
        "detected_skills": skills,
        "market_demand": [
            {
                "role": role,
                "demand_score": 70 if skills else 45,
                "trend": "Add a Gemini key for live AI-ranked demand signals.",
            },
            {
                "role": f"Junior {role}",
                "demand_score": 62 if skills else 38,
                "trend": "Entry-level options improve with role-specific projects.",
            },
        ],
        "top_roles": [
            {
                "title": role,
                "fit_score": 70 if skills else 45,
                "why": "Based on your entered interest and skills.",
                "growth_signal": "Build proof-of-work projects and refine your resume.",
            }
        ],
        "selected_role": role,
        "why_this_role": [
            "This direction matches the interest and skills you entered.",
            "A complete resume and Gemini API key will make this explanation more precise.",
        ],
        "required_skills": skills[:4] + missing[:3],
        "target_companies": [
            "Product companies hiring for this role",
            "Service companies with relevant teams",
            "Startups building in this domain",
        ],
        "skill_gap": {
            "strong_skills": skills[:6],
            "missing_skills": missing,
            "readiness_score": 55 if skills else 25,
        },
        "skill_match": {
            "matched": skills[:6],
            "missing": missing,
        },
        "recommended_skills": missing,
        "top_career_options": [
            {"title": role, "fit_score": 70 if skills else 45},
            {"title": f"Associate {role}", "fit_score": 62 if skills else 36},
            {"title": "Project-based Internship", "fit_score": 58 if skills else 32},
        ],
        "learning_plan": [
            {
                "phase": "Foundation",
                "duration": "2 weeks",
                "actions": "Revise fundamentals and learn the first missing skill.",
            },
            {
                "phase": "Portfolio",
                "duration": "4 weeks",
                "actions": "Build one public, documented project aligned to your target role.",
            },
            {
                "phase": "Interview",
                "duration": "2 weeks",
                "actions": "Practice technical questions and prepare project explanations.",
            },
        ],
        "projects": [
            {
                "title": "AI Career Portfolio Project",
                "level": "Intermediate",
                "description": "Build a deployable project that proves your role-specific skills.",
                "success_metrics": ["GitHub repo", "live demo", "clear README", "measurable outcome"],
            }
        ],
        "resume_feedback": [
            "Use role-specific keywords from your target jobs.",
            "Rewrite project bullets with action, technology, and measurable impact.",
            "Add public links for GitHub, demo, and portfolio.",
        ],
        "market_insights": [
            "Hiring favors candidates with practical projects and clear communication.",
            "Target internships, junior roles, and freelance projects that match your strongest skills.",
        ],
        "next_actions": [
            "Retry the analysis with a shorter resume/profile." if key_configured else "Add your Gemini API key.",
            "Paste a complete resume or profile.",
            "Generate a fresh personalized plan.",
        ],
    }


def generate_career_intelligence(payload):
    api_key = _get_api_key()
    fallback = fallback_profile(payload, key_configured=gemini_configured())
    if not gemini_configured():
        return fallback, False, "GEMINI_API_KEY is not configured. Showing local fallback guidance."

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

    return parsed, True, None


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
