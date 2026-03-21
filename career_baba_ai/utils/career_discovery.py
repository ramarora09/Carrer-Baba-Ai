import streamlit as st
from utils.career_model import train_career_model, predict_role
from utils.market_analysis import get_role_skills, get_role_companies


def run_career_discovery():

    st.header(" Career Discovery")

    # Field selection
    field = st.selectbox(
        "Select Your Field",
        ["AI/ML", "Web Development", "App Development", "Cloud", "Cyber Security"]
    )

    # Field → Roles mapping
    roles_map = {
        "AI/ML": ["Data Scientist", "ML Engineer", "AI Engineer"],
        "Web Development": ["Frontend Developer", "Backend Developer", "Full Stack Developer"],
        "App Development": ["Android Developer", "Flutter Developer"],
        "Cloud": ["Cloud Engineer", "DevOps Engineer"],
        "Cyber Security": ["Security Analyst", "Ethical Hacker"]
    }

    if field:

        roles = roles_map[field]

        st.subheader(" Job Roles")

        for role in roles:
            st.write(f" {role}")

        # Show skills + companies for first role
        selected_role = roles[0]

        role_skills = get_role_skills(selected_role)
        companies = get_role_companies(selected_role)

        st.subheader(" Required Skills")
        st.write(role_skills)

        st.subheader(" Top Companies")
        st.write(", ".join(companies))

        st.divider()

        st.subheader(" Try AI Prediction")

        manual_skills = st.text_input("Enter your skills (optional)")

        if manual_skills:

            user_skills = [s.strip().lower() for s in manual_skills.split(",")]

            model, vectorizer = train_career_model()
            predicted_role, confidence = predict_role(model, vectorizer, user_skills)

            st.success(f"AI Suggests: {predicted_role}")
            st.write(f"Confidence: {round(confidence,2)}%")

            # Skill gap
            matched = [s for s in role_skills if s in user_skills]
            missing = [s for s in role_skills if s not in user_skills]

            st.subheader(" Skill Gap")
            st.write(f" You have: {matched}")
            st.write(f" You need: {missing}")