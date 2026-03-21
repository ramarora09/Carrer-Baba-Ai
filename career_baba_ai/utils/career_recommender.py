from utils.role_data import ROLE_DATA

def recommend_roles(user_skills):
    role_scores={}

    for role, data in ROLE_DATA.items():
        role_skills=data["skills"]
        matched=0

        for skill in role_skills:
            if skill in user_skills:
                matched+=1

        score=(matched / len(role_skills))*100

        role_scores[role]=round(score,2)

    soretd_roles=sorted(role_scores.items(),key=lambda x:x[1],reverse=True)

    return soretd_roles[:3]