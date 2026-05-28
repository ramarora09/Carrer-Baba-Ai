import math
import re
from collections import Counter


SKILL_ALIASES = {
    "python": ["python", "pandas", "numpy", "scikit", "sklearn", "matplotlib", "seaborn"],
    "sql": ["sql", "mysql", "postgres", "postgresql", "sqlite", "database"],
    "machine learning": ["machine learning", "ml", "classification", "regression", "clustering", "model training"],
    "deep learning": ["deep learning", "neural network", "tensorflow", "pytorch", "keras"],
    "nlp": ["nlp", "natural language", "text classification", "transformer", "bert", "llm"],
    "data visualization": ["power bi", "tableau", "dashboard", "visualization", "charts"],
    "statistics": ["statistics", "probability", "hypothesis", "a/b testing", "linear algebra"],
    "excel": ["excel", "spreadsheet", "pivot"],
    "react": ["react", "next.js", "nextjs", "frontend"],
    "javascript": ["javascript", "typescript", "node", "node.js", "express"],
    "html/css": ["html", "css", "tailwind", "bootstrap"],
    "fastapi": ["fastapi", "flask", "django", "api"],
    "cloud": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes"],
    "cybersecurity": ["cybersecurity", "network security", "penetration", "owasp", "siem"],
    "devops": ["devops", "ci/cd", "github actions", "linux", "terraform"],
    "communication": ["communication", "presentation", "teamwork", "leadership"],
}


ROLE_PROFILES = [
    {
        "title": "AI/ML Engineer",
        "keywords": "ai ml machine learning deep learning python nlp model training deployment api cloud",
        "required_skills": ["python", "machine learning", "deep learning", "nlp", "statistics", "fastapi", "cloud"],
        "companies": ["AI product startups", "SaaS companies with ML teams", "Fintech analytics teams"],
        "base_demand": 86,
    },
    {
        "title": "Data Scientist",
        "keywords": "data science statistics python sql machine learning analytics experiment visualization",
        "required_skills": ["python", "sql", "machine learning", "statistics", "data visualization", "communication"],
        "companies": ["Analytics consultancies", "Product companies", "E-commerce and fintech teams"],
        "base_demand": 84,
    },
    {
        "title": "Data Analyst",
        "keywords": "data analyst sql excel dashboard power bi tableau reporting business analytics",
        "required_skills": ["sql", "excel", "data visualization", "statistics", "communication"],
        "companies": ["Operations teams", "Business intelligence teams", "Service companies"],
        "base_demand": 78,
    },
    {
        "title": "Full Stack Developer",
        "keywords": "full stack web developer react javascript backend api database fastapi node",
        "required_skills": ["javascript", "react", "html/css", "fastapi", "sql", "cloud"],
        "companies": ["Web product companies", "Digital agencies", "Early-stage startups"],
        "base_demand": 82,
    },
    {
        "title": "Backend Developer",
        "keywords": "backend developer api python fastapi django database sql cloud system design",
        "required_skills": ["python", "fastapi", "sql", "cloud", "devops"],
        "companies": ["SaaS backend teams", "Platform engineering teams", "Fintech product teams"],
        "base_demand": 80,
    },
    {
        "title": "Cybersecurity Analyst",
        "keywords": "cybersecurity security analyst network owasp siem linux incident response risk",
        "required_skills": ["cybersecurity", "sql", "cloud", "devops", "communication"],
        "companies": ["Security operations centers", "Banks and fintech firms", "Managed security providers"],
        "base_demand": 79,
    },
]


def generate_local_career_intelligence(payload):
    text = _payload_text(payload)
    detected_skills = _extract_skills(text, payload.get("skills", ""))
    target_role = (payload.get("target_role") or "").strip()
    matches = _rank_roles(text, detected_skills, target_role)
    selected = matches[0]
    required = selected["required_skills"]
    matched = [skill for skill in required if skill in detected_skills]
    missing = [skill for skill in required if skill not in detected_skills]
    readiness = _readiness_score(matched, required, payload)

    return {
        "profile_summary": _profile_summary(payload, selected, detected_skills, readiness),
        "detected_skills": detected_skills,
        "market_demand": _market_demand(matches, detected_skills),
        "top_roles": [
            {
                "title": role["title"],
                "fit_score": role["fit_score"],
                "why": role["why"],
                "growth_signal": role["growth_signal"],
            }
            for role in matches[:3]
        ],
        "selected_role": selected["title"],
        "why_this_role": _why_role(selected, matched, missing, target_role),
        "required_skills": required,
        "target_companies": selected["companies"],
        "skill_gap": {
            "strong_skills": matched or detected_skills[:6],
            "missing_skills": missing,
            "readiness_score": readiness,
        },
        "skill_match": {
            "matched": matched,
            "missing": missing,
        },
        "recommended_skills": missing[:5],
        "top_career_options": [
            {"title": role["title"], "fit_score": role["fit_score"]}
            for role in matches[:4]
        ],
        "learning_plan": _learning_plan(missing, payload),
        "projects": _projects_for_role(selected["title"], missing),
        "resume_feedback": _resume_feedback(text, detected_skills),
        "market_insights": _market_insights(selected, missing),
        "next_actions": _next_actions(selected, missing),
        "engine": "local_skill_vector_model",
    }


def _payload_text(payload):
    parts = [
        payload.get("resume_text", ""),
        payload.get("interest", ""),
        payload.get("experience", ""),
        payload.get("goal", ""),
        payload.get("time_plan", ""),
        payload.get("target_role", ""),
        payload.get("skills", ""),
        payload.get("background", ""),
    ]
    return " ".join(str(part) for part in parts if part).lower()


def _extract_skills(text, explicit_skills):
    detected = []
    explicit = {item.strip().lower() for item in str(explicit_skills).split(",") if item.strip()}

    for skill, aliases in SKILL_ALIASES.items():
        if skill in explicit or any(alias in text for alias in aliases):
            detected.append(skill)

    for item in explicit:
        if item and item not in detected:
            detected.append(item)

    return detected[:12]


def _rank_roles(text, detected_skills, target_role):
    documents = [text] + [role["keywords"] + " " + " ".join(role["required_skills"]) for role in ROLE_PROFILES]
    vectors = [_tfidf_vector(documents, document) for document in documents]
    user_vector = vectors[0]

    ranked = []
    for index, role in enumerate(ROLE_PROFILES, start=1):
        similarity = _cosine(user_vector, vectors[index])
        skill_overlap = len(set(detected_skills) & set(role["required_skills"])) / max(len(role["required_skills"]), 1)
        target_bonus = 0.12 if target_role and _normal(target_role) in _normal(role["title"]) else 0
        fit = round(min(96, 30 + similarity * 42 + skill_overlap * 34 + target_bonus * 100))
        matched = sorted(set(detected_skills) & set(role["required_skills"]))
        missing = [skill for skill in role["required_skills"] if skill not in detected_skills]
        ranked.append(
            {
                **role,
                "fit_score": fit,
                "matched": matched,
                "missing": missing,
                "why": _fit_reason(role, matched, missing),
                "growth_signal": _growth_signal(missing),
            }
        )

    return sorted(ranked, key=lambda item: item["fit_score"], reverse=True)


def _tfidf_vector(all_documents, document):
    tokens = _tokens(document)
    counts = Counter(tokens)
    vector = {}
    total_documents = len(all_documents)
    for token, count in counts.items():
        containing = sum(1 for candidate in all_documents if token in set(_tokens(candidate)))
        idf = math.log((1 + total_documents) / (1 + containing)) + 1
        vector[token] = count * idf
    return vector


def _tokens(text):
    return [token for token in re.findall(r"[a-z0-9+#.]+", text.lower()) if len(token) > 2]


def _cosine(left, right):
    common = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0
    return numerator / (left_norm * right_norm)


def _normal(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _readiness_score(matched, required, payload):
    base = len(matched) / max(len(required), 1)
    experience = str(payload.get("experience", "")).lower()
    experience_bonus = {"beginner": 0, "intermediate": 8, "advanced": 14}.get(experience, 4)
    background_bonus = 8 if payload.get("background") or payload.get("resume_text") else 0
    return round(min(95, 25 + base * 58 + experience_bonus + background_bonus))


def _profile_summary(payload, selected, skills, readiness):
    goal = payload.get("goal") or "career growth"
    skill_text = ", ".join(skills[:5]) if skills else "your current profile inputs"
    return (
        f"Career Baba AI identifies {selected['title']} as your strongest direction for {goal}. "
        f"The recommendation is based on your skills, role requirements, resume/background signals, "
        f"and readiness scoring. Current readiness is {readiness}% using signals from {skill_text}."
    )


def _market_demand(matches, detected_skills):
    demand = []
    for role in matches[:3]:
        skill_boost = min(8, len(set(detected_skills) & set(role["required_skills"])) * 2)
        score = min(95, role["base_demand"] + skill_boost - len(role["missing"]))
        demand.append(
            {
                "role": role["title"],
                "demand_score": score,
                "trend": "Strong demand when paired with projects, deployable proof of work, and clear resume keywords.",
            }
        )
    return demand


def _why_role(role, matched, missing, target_role):
    reasons = [
        f"Your profile has the strongest vector similarity with {role['title']} among the available role profiles.",
        f"Matched skills: {', '.join(matched) if matched else 'not enough explicit skills yet'}.",
    ]
    if target_role:
        reasons.append(f"Your stated target role was considered as an extra ranking signal.")
    if missing:
        reasons.append(f"The fastest improvement area is: {', '.join(missing[:3])}.")
    return reasons


def _fit_reason(role, matched, missing):
    if matched:
        return f"Matches {', '.join(matched[:4])}; improve {', '.join(missing[:3]) if missing else 'portfolio depth'} for stronger fit."
    return f"Role matches your interest/background text, but explicit skills for {role['title']} are still thin."


def _growth_signal(missing):
    if not missing:
        return "You can shift focus from learning basics to building proof-of-work projects."
    return f"Learning {missing[0]} next will increase readiness quickly."


def _learning_plan(missing, payload):
    time_plan = payload.get("time_plan") or "3-6 months"
    first = missing[0] if missing else "portfolio polish"
    second = missing[1] if len(missing) > 1 else "interview storytelling"
    third = missing[2] if len(missing) > 2 else "deployment and documentation"
    return [
        {"phase": "Foundation", "duration": "2-3 weeks", "actions": f"Strengthen {first} with notes, mini exercises, and one small demo."},
        {"phase": "Applied Project", "duration": "3-5 weeks", "actions": f"Build a role-specific project using {first} and {second}."},
        {"phase": "Job Readiness", "duration": time_plan, "actions": f"Polish resume keywords, deploy your project, and practice explaining {third}."},
    ]


def _projects_for_role(role_title, missing):
    project_map = {
        "AI/ML Engineer": "Train and deploy a resume-to-role recommendation API with explainable skill-gap scoring.",
        "Data Scientist": "Create an end-to-end churn or placement prediction notebook with model evaluation and dashboard.",
        "Data Analyst": "Build a hiring market dashboard with SQL queries, Excel/BI visuals, and business recommendations.",
        "Full Stack Developer": "Build a full-stack career tracker with auth, dashboards, API routes, and database storage.",
        "Backend Developer": "Create a production-style API with auth, database models, tests, and Docker deployment.",
        "Cybersecurity Analyst": "Create a security audit lab with OWASP checks, logs, and incident-response notes.",
    }
    focus = missing[0] if missing else "deployment"
    return [
        {
            "title": f"{role_title} Proof-of-Work Project",
            "level": "Intermediate",
            "description": project_map.get(role_title, "Build a role-specific portfolio project with measurable outcomes."),
            "success_metrics": ["GitHub repo", "live demo or screenshots", f"Clear use of {focus}", "README with results"],
        }
    ]


def _resume_feedback(text, detected_skills):
    feedback = []
    if len(text) < 250:
        feedback.append("Add more resume/background detail so the advisor has stronger signals.")
    if not re.search(r"\d+%|\d+x|\d+\+", text):
        feedback.append("Add measurable impact such as accuracy, users, response time, cost saved, or project scale.")
    if len(detected_skills) < 4:
        feedback.append("List technical skills explicitly; hidden skills are harder for both recruiters and models to detect.")
    feedback.append("Rewrite project bullets with action, technology, and outcome.")
    feedback.append("Add GitHub, portfolio, deployed demo, or certification links where possible.")
    return feedback[:5]


def _market_insights(selected, missing):
    insight = f"{selected['title']} hiring rewards candidates who can show practical projects, clean communication, and job-specific tooling."
    if missing:
        return [insight, f"Your biggest market gap is {missing[0]}; close it with one visible portfolio project."]
    return [insight, "Your next market advantage is deeper project quality rather than more beginner certificates."]


def _next_actions(selected, missing):
    actions = [
        f"Build one {selected['title']} project and publish it.",
        "Update your resume with matched role keywords.",
        "Practice explaining your project decisions in interview format.",
    ]
    if missing:
        actions.insert(0, f"Learn {missing[0]} with a small applied demo this week.")
    return actions[:4]
