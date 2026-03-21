def recommend_skills(missing_skills):

    # Priority mapping (core skills first 🔥)
    PRIORITY_SKILLS = [
        "python", "java", "javascript",
        "sql", "dsa", "machine learning",
        "react", "node", "docker", "aws"
    ]

    recommendations = []

    # Step 1: High priority skills first
    for skill in PRIORITY_SKILLS:
        if skill in missing_skills:
            recommendations.append(skill)

    # Step 2: Add remaining skills
    for skill in missing_skills:
        if skill not in recommendations:
            recommendations.append(skill)

    # Step 3: Limit output
    return recommendations[:5]