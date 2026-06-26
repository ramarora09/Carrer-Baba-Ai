import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

try:
    from career_baba_ai.utils.local_ml_engine import generate_local_career_intelligence
    from career_baba_ai.utils.rag_engine import format_rag_context, retrieve_career_context
except ModuleNotFoundError:
    from utils.local_ml_engine import generate_local_career_intelligence
    from utils.rag_engine import format_rag_context, retrieve_career_context


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
    return os.getenv("ENABLE_GEMINI_ENHANCEMENT", "true").lower() != "false"


def generate_career_intelligence(payload):
    api_key = _get_api_key()
    fallback = generate_local_career_intelligence(payload)
    rag_context = retrieve_career_context(
        query=f"{payload.get('target_role', '')} {payload.get('interest', '')} {payload.get('goal', '')}",
        profile=payload,
        top_k=5,
    )
    if not gemini_enhancement_enabled():
        fallback["rag_sources"] = _rag_sources(rag_context)
        return fallback, False, "AI guidance generated from your profile signals and career knowledge base."

    if not gemini_configured():
        fallback["rag_sources"] = _rag_sources(rag_context)
        return fallback, False, "AI guidance generated from your profile signals and career knowledge base."

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

Profile signal analysis:
{json.dumps(fallback, indent=2)}

Retrieved career knowledge:
{format_rag_context(rag_context)}

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
  "next_actions": ["string"],
  "rag_sources": [
    {{
      "title": "string",
      "category": "string"
    }}
  ]
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
        return fallback, False, f"Live AI advisor request failed. Guidance was generated from your profile signals. {exc.reason}"

    text = "".join(
        part.get("text", "")
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    )
    parsed = _extract_json(text)
    if not parsed:
        candidate = data.get("candidates", [{}])[0]
        finish_reason = candidate.get("finishReason")
        reason = f" Finish reason: {finish_reason}." if finish_reason else ""
        return fallback, False, f"Live AI advisor returned an incomplete response.{reason} Guidance was generated from your profile signals."

    parsed["engine"] = "gemini_career_advisor"
    parsed["rag_sources"] = _rag_sources(rag_context)

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

    return parsed, True, "AI guidance generated successfully."


def generate_career_chat_reply(message, profile=None):
    profile = profile or {}
    fallback = generate_local_career_intelligence(profile)
    rag_context = retrieve_career_context(query=message, profile=profile, top_k=5)

    if not gemini_configured():
        return _fallback_chat_reply(message, fallback, rag_context), False

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    encoded_model = urllib.parse.quote(model, safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{encoded_model}:generateContent"

    prompt = f"""
You are Career Baba AI, a professional career guidance chatbot for students, freshers, and early-career users.

Answer the user's question directly and practically. Use the profile context when useful. Recommend roles,
skills, projects, resume improvements, interview preparation, learning resources, or next steps only when they
fit the question. Keep the answer friendly, specific, and action-oriented.

User profile:
{json.dumps(profile, indent=2)}

Profile signal analysis:
{json.dumps(fallback, indent=2)}

Retrieved career knowledge:
{format_rag_context(rag_context)}

User question:
{message}
"""

    body = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Be concise, practical, and supportive. Do not mention internal implementation details. "
                        "Do not claim guaranteed jobs, salaries, or admissions."
                    )
                }
            ]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.45,
            "maxOutputTokens": 1400,
        },
    }

    if os.getenv("ENABLE_GEMINI_SEARCH", "").lower() == "true":
        body["tools"] = [{"google_search": {}}]

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": _get_api_key(),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return _fallback_chat_reply(message, fallback, rag_context), False
    except urllib.error.URLError as exc:
        return _fallback_chat_reply(message, fallback, rag_context), False

    text = "".join(
        part.get("text", "")
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    ).strip()
    if not text:
        return "The AI advisor could not generate a useful reply. Please ask again with a little more detail.", False

    return text, True


def _fallback_chat_reply(message, analysis, rag_context=None):
    rag_context = rag_context or []
    selected_role = analysis.get("selected_role", "your target role")
    detected = analysis.get("detected_skills", [])
    skill_gap = analysis.get("skill_gap", {})
    missing = skill_gap.get("missing_skills", [])
    projects = analysis.get("projects", [])
    roadmap = analysis.get("learning_plan", [])
    resume_feedback = analysis.get("resume_feedback", [])
    lower_message = message.lower()

    if "resume" in lower_message or "cv" in lower_message:
        focus = resume_feedback[:3] or [
            "Add measurable project outcomes.",
            "Use role-specific keywords from the job description.",
            "Show GitHub, portfolio, deployed demos, or certifications where possible.",
        ]
        return _format_lines(
            "Here is how to improve your resume:",
            focus,
            _closing_with_source(
                f"Target it toward {selected_role} and keep each project bullet focused on action, technology, and result.",
                rag_context,
            ),
        )

    if "project" in lower_message or "portfolio" in lower_message:
        project = projects[0] if projects else {}
        title = project.get("title", f"{selected_role} portfolio project")
        description = project.get("description", "Build one practical project that proves your role-specific skills.")
        metrics = project.get("success_metrics", ["GitHub repo", "live demo", "clear README"])
        return _format_lines(
            f"Build this project first: {title}",
            [description, *metrics],
            _closing_with_source(
                "One strong finished project is more useful than many unfinished tutorials.",
                rag_context,
            ),
        )

    if "learn" in lower_message or "skill" in lower_message or "roadmap" in lower_message:
        actions = [f"Learn {skill}" for skill in missing[:4]]
        if not actions:
            actions = [item.get("actions", "") for item in roadmap if item.get("actions")]
        return _format_lines(
            f"For {selected_role}, focus on these next steps:",
            actions or ["Strengthen your portfolio, interview explanations, and deployment practice."],
            _closing_with_source(
                "After each skill, make a small proof-of-work project so your learning is visible.",
                rag_context,
            ),
        )

    if "interview" in lower_message:
        return _format_lines(
            f"To prepare for {selected_role} interviews:",
            [
                "Prepare a 60-second intro connected to your target role.",
                "Practice explaining your best project: problem, tools, decisions, result.",
                f"Revise the missing skills: {', '.join(missing[:3]) if missing else 'role fundamentals and project depth'}.",
                "Do mock questions every day and write better answers after each attempt.",
            ],
            _closing_with_source("The goal is to sound practical, not memorized.", rag_context),
        )

    strengths = ", ".join(detected[:5]) if detected else "your current profile details"
    next_skills = ", ".join(missing[:4]) if missing else "portfolio depth and interview practice"
    return (
        f"Based on your profile, {selected_role} looks like a strong direction.\n\n"
        f"Your current signals: {strengths}.\n"
        f"Next improvement areas: {next_skills}.\n\n"
        "Best next move: build one role-focused project, update your resume with measurable outcomes, "
        f"and practice explaining your project decisions clearly.\n\n{_source_line(rag_context)}"
    )


def _format_lines(title, items, closing):
    clean_items = [str(item).strip() for item in items if str(item).strip()]
    bullet_text = "\n".join(f"- {item}" for item in clean_items)
    return f"{title}\n\n{bullet_text}\n\n{closing}"


def _closing_with_source(closing, rag_context):
    source_line = _source_line(rag_context)
    if not source_line:
        return closing
    return f"{closing}\n\n{source_line}"


def _source_line(rag_context):
    if not rag_context:
        return ""
    titles = ", ".join(item["title"] for item in rag_context[:2])
    return f"Grounded with: {titles}."


def _rag_sources(rag_context):
    return [
        {
            "title": item["title"],
            "category": item["category"],
        }
        for item in rag_context[:5]
    ]


def _format_gemini_error(status_code, detail):
    message = "Live AI advisor request failed. Guidance was generated from your profile signals."
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
