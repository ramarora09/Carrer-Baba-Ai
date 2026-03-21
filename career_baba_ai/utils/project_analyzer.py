from utils.role_data import ROLE_DATA

# ---------------- PROJECT RELEVANCE CHECK ----------------
def analyze_projects(user_projects, role):

    role_skills = ROLE_DATA.get(role, {}).get("skills", [])

    relevant = []
    not_relevant = []

    for project in user_projects:
        match_found = False

        for skill in role_skills:
            if skill.lower() in project.lower():
                match_found = True
                break

        if match_found:
            relevant.append(project)
        else:
            not_relevant.append(project)

    return relevant, not_relevant


# ---------------- PROJECT SUGGESTIONS ----------------
SKILL_PROJECT_MAP = {

    "python": ["Data Analysis Project", "Automation Script"],
    "machine learning": ["House Price Prediction", "Spam Classifier", "Recommendation System"],
    "deep learning": ["Image Classifier", "Neural Network Project"],
    "nlp": ["Chatbot", "Sentiment Analysis"],

    "html": ["Portfolio Website"],
    "css": ["Landing Page"],
    "javascript": ["To-Do App", "Weather App"],
    "react": ["Dashboard UI"],
    "node": ["REST API"],
    "mongodb": ["Full Stack App"],

    "java": ["Spring Boot API"],
    "docker": ["Dockerized App"],
    "aws": ["Cloud Deployment"],
    "kubernetes": ["CI/CD Pipeline"],

    "android": ["Android App"],
    "kotlin": ["Notes App"],
    "swift": ["iOS App"],

    "c++": ["Game Engine Basics"],
    "unity": ["2D Game"],
    "unreal": ["3D Game"]
}


def suggest_projects(role):

    role_skills = ROLE_DATA.get(role, {}).get("skills", [])

    suggested_projects = set()

    for skill in role_skills:
        skill = skill.lower()

        for key in SKILL_PROJECT_MAP:
            if key in skill:
                suggested_projects.update(SKILL_PROJECT_MAP[key])

    if not suggested_projects:
        return ["Build real-world projects based on your domain"]

    return list(suggested_projects)