import streamlit as st
from utils.career_model import train_career_model, predict_role
from utils.market_analysis import get_role_skills, get_role_companies
from utils.recommendation import recommend_skills
from utils.roadmap import generate_roadmap
from utils.explainer import explain_prediction
from utils.role_data import ROLE_DATA
from utils.project_analyzer import suggest_projects


def run_manual_mode():

    st.header("Career Exploration + AI Guidance")

    # ---------------- USER PROFILE INPUT ----------------
    st.subheader("Your Career Profile")

    interest = st.selectbox("Your Interest Area", [
        "AI/ML", "Web Development", "App Development",
        "Cloud", "Cyber Security", "Data"
    ])

    experience = st.selectbox("Experience Level", [
        "Beginner", "Intermediate", "Advanced"
    ])

    goal = st.selectbox("Your Goal", [
        "Internship", "Job", "Freelancing"
    ])

    time = st.selectbox("Time Available", [
        "1-2 months", "3-6 months", "6+ months"
    ])

    st.divider()

    # ---------------- ROLE SELECTION ----------------
    roles = list(ROLE_DATA.keys())

    selected_role = st.selectbox("Select Target Role", roles)

    role_skills = get_role_skills(selected_role)
    companies = get_role_companies(selected_role)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Required Skills")
        for s in role_skills:
            st.write(s)

    with col2:
        st.subheader("Top Companies")
        for c in companies:
            st.write(c)

    st.divider()

    # ---------------- USER SKILLS ----------------
    skills_input = st.text_input("Enter your skills (comma separated)")

    if skills_input:

        user_skills = [s.strip().lower() for s in skills_input.split(",")]

        st.subheader("Your Skills")
        st.write(user_skills)

        # ML Prediction
        model, vectorizer = train_career_model()
        predicted_role, confidence = predict_role(model, vectorizer, user_skills)

        st.subheader("AI Suggested Role")
        st.write(predicted_role)
        st.write(f"Confidence: {round(confidence,2)}%")

        # Explanation
        st.subheader("Why this role?")
        explanation = explain_prediction(user_skills, role_skills)

        for e in explanation:
            st.write(e)

        # Skill Gap
        matched = [s for s in role_skills if s in user_skills]
        missing = [s for s in role_skills if s not in user_skills]

        st.subheader("Skill Gap")

        st.write("You have:", matched)
        st.write("You need:", missing)

        # Readiness
        score = (len(matched) / len(role_skills)) * 100 if role_skills else 0

        st.subheader("Career Readiness")
        st.progress(int(score))
        st.write(f"{round(score,2)}% Ready")

        # ---------------- SMART CAREER GUIDANCE 🔥 ----------------
        st.subheader("Career Guidance")

        if experience == "Beginner":
            st.write("Start with fundamentals and build 1-2 beginner projects.")

        elif experience == "Intermediate":
            st.write("Focus on real-world projects and strengthen your portfolio.")

        else:
            st.write("Focus on advanced concepts, system design, and job preparation.")

        if goal == "Internship":
            st.write("Build 2-3 strong projects and apply consistently.")

        elif goal == "Job":
            st.write("Focus on DSA, projects, and interview preparation.")

        else:
            st.write("Build client-based projects and freelance portfolio.")

        if time == "1-2 months":
            st.write("Focus on basics + 1 project.")

        elif time == "3-6 months":
            st.write("Learn + build 2-3 projects + apply.")

        else:
            st.write("Advanced learning + internships + real-world experience.")

        # Recommendations
        st.subheader("Skills to Learn")

        recommendations = recommend_skills(missing)

        for skill in recommendations:
            st.write(skill)

        # ---------------- PROJECTS 🔥 ----------------
        st.subheader("Recommended Projects")

        projects = suggest_projects(selected_role)

        for p in projects:
            st.write(p)

        # ---------------- ROADMAP ----------------
        st.subheader("Career Roadmap")

        roadmap = generate_roadmap(selected_role, missing)

        for step in roadmap:
            st.write(step)

        # ---------------- FINAL SUMMARY 🔥 ----------------
        st.subheader("Final Career Summary")

        st.write(f"Target Role: {selected_role}")
        st.write(f"Experience Level: {experience}")
        st.write(f"Goal: {goal}")
        st.write(f"Time Plan: {time}")

        st.success("Follow this roadmap consistently to achieve your goal.")