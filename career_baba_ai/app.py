import os
import tempfile
import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

try:
    from career_baba_ai.utils.gemini_client import gemini_configured, generate_career_intelligence
    from career_baba_ai.utils.resume_parser import extract_text_from_pdf
except ModuleNotFoundError:
    from utils.gemini_client import gemini_configured, generate_career_intelligence
    from utils.resume_parser import extract_text_from_pdf


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSION_COOKIE = "career_baba_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7

load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI(title="Career Baba AI", version="2.0.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _auth_secret():
    return os.getenv("AUTH_SECRET", "career-baba-dev-secret-change-me")


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as users_file:
        return json.load(users_file)


def _save_users(users):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as users_file:
        json.dump(users, users_file, indent=2)


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return f"{salt}${password_hash}"


def _verify_password(password, stored):
    try:
        salt, expected_hash = stored.split("$", 1)
    except ValueError:
        return False

    candidate = _hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, expected_hash)


def _sign_session(email):
    expires = int(time.time()) + SESSION_MAX_AGE
    payload = f"{email}|{expires}"
    signature = hmac.new(
        _auth_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    token = f"{payload}|{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(token).decode("utf-8")


def _read_session(request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None

    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        email, expires, signature = decoded.rsplit("|", 2)
    except (ValueError, UnicodeDecodeError):
        return None

    payload = f"{email}|{expires}"
    expected_signature = hmac.new(
        _auth_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        expires_at = int(expires)
    except ValueError:
        return None

    if expires_at < int(time.time()):
        return None

    return email


def _current_user(request):
    email = _read_session(request)
    if not email:
        return None

    return _load_users().get(email)


def _require_user(request):
    user = _current_user(request)
    if not user:
        return None
    return user


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = _current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "gemini_configured": gemini_configured(),
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
            "user": user,
        },
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _current_user(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"mode": "login", "error": None},
    )


@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    normalized_email = email.strip().lower()
    user = _load_users().get(normalized_email)
    if not user or not _verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"mode": "login", "error": "Invalid email or password."},
            status_code=400,
        )

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        _sign_session(normalized_email),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if _current_user(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"mode": "register", "error": None},
    )


@app.post("/register")
async def register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    normalized_email = email.strip().lower()
    users = _load_users()

    if normalized_email in users:
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"mode": "register", "error": "An account with this email already exists."},
            status_code=400,
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"mode": "register", "error": "Password must be at least 6 characters."},
            status_code=400,
        )

    users[normalized_email] = {
        "name": name.strip() or normalized_email,
        "email": normalized_email,
        "password_hash": _hash_password(password),
        "created_at": int(time.time()),
    }
    _save_users(users)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        _sign_session(normalized_email),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.post("/api/analyze")
@app.post("/api/analyze/")
async def analyze(request: Request):
    if not _require_user(request):
        return JSONResponse({"error": "Authentication required."}, status_code=401)

    payload = await request.json()
    result, ai_used, notice = generate_career_intelligence(payload)
    return JSONResponse({"result": result, "ai_used": ai_used, "notice": notice})


@app.post("/api/resume")
@app.post("/api/resume/")
async def analyze_resume(
    request: Request,
    file: UploadFile | None = File(default=None),
    resume_text: str = Form(default=""),
    interest: str = Form(default=""),
    experience: str = Form(default=""),
    goal: str = Form(default=""),
    time_plan: str = Form(default=""),
    target_role: str = Form(default=""),
    skills: str = Form(default=""),
    background: str = Form(default=""),
):
    if not _require_user(request):
        return JSONResponse({"error": "Authentication required."}, status_code=401)

    text = resume_text.strip()

    if file and file.filename and file.filename.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as pdf_file:
                text = extract_text_from_pdf(pdf_file)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    payload = {
        "resume_text": text,
        "interest": interest,
        "experience": experience,
        "goal": goal,
        "time_plan": time_plan,
        "target_role": target_role,
        "skills": skills,
        "background": background,
    }

    result, ai_used, notice = generate_career_intelligence(payload)
    return JSONResponse({"result": result, "ai_used": ai_used, "notice": notice})


@app.get("/api/resume")
@app.get("/api/resume/")
async def resume_endpoint_info():
    return JSONResponse(
        {"status": "ok", "message": "Use POST /api/resume to analyze a resume."}
    )


@app.get("/api/health")
async def health():
    root_env = os.path.join(os.path.dirname(BASE_DIR), ".env")
    app_env = os.path.join(BASE_DIR, ".env")
    return {
        "status": "ok",
        "gemini_configured": gemini_configured(),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        "env_files_checked": [root_env, app_env],
        "env_file_found": os.path.exists(root_env) or os.path.exists(app_env),
    }
