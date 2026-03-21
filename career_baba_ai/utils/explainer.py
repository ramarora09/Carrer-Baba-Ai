def explain_prediction(user_skills, role_skills):

    matched = list(set(user_skills) & set(role_skills))

    explanation = []

    for skill in matched:
        explanation.append(f"{skill} matches industry requirements")

    return explanation