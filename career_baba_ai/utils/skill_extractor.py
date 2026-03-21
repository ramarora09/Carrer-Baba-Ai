def extract_skills(text, skill_list):
    found_skills = []
    for skill in skill_list:
        if skill.lower() in text:
            found_skills.append(skill)
    return found_skills