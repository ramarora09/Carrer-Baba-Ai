import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.career_model import train_career_model, predict_role
from utils.resume_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.market_analysis import calculate_role_demand, get_role_skills, get_role_companies
from utils.recommendation import recommend_skills  
from utils.roadmap import generate_roadmap
from utils.manual import run_manual_mode
from utils.explainer import explain_prediction
from utils.project_analyzer import suggest_projects
from utils.role_data import ROLE_DATA

st.set_page_config(page_title="Career Baba", layout="wide")

st.title("Career Baba - AI Career Advisor")

mode = st.sidebar.radio(
    "Choose Mode",
    ["Resume Analysis", "Manual Career Guidance"]
)

# Market Demand
st.subheader("Market Demand (Top Roles)")
demand_df = calculate_role_demand()
st.dataframe(demand_df)

st.divider()

# ---------------- MANUAL MODE ----------------
if mode == "Manual Career Guidance":
    run_manual_mode()

# ---------------- RESUME MODE ----------------
if mode == "Resume Analysis":

    st.header("Resume Analysis Dashboard")

    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file:

        text = extract_text_from_pdf(uploaded_file)

        skills_df = pd.read_csv("skill_dataset.csv")
        skill_list = skills_df["skill"].tolist()

        user_skills = extract_skills(text, skill_list)

        st.subheader("Extracted Skills")
        st.success(user_skills)

        if len(user_skills) == 0:
            st.warning("No skills detected from resume")
            st.stop()

        # ML Prediction
        model, vectorizer = train_career_model()
        predicted_role, confidence = predict_role(model, vectorizer, user_skills)

        # ROLE OVERRIDE (NEW 🔥)
        st.subheader("Select Target Role (Optional)")
        roles = list(ROLE_DATA.keys())
        selected_option = st.selectbox("Choose Role", ["Auto Detect"] + roles)

        if selected_option == "Auto Detect":
            selected_role = predicted_role
        else:
            selected_role = selected_option

        st.subheader("AI Career Prediction")
        st.write("Predicted Role:", predicted_role)
        st.write("Selected Role:", selected_role)
        st.write(f"Confidence: {round(confidence,2)}%")

        # Explanation
        st.subheader("Why this role?")
        role_skills = get_role_skills(selected_role)
        explanation = explain_prediction(user_skills, role_skills)

        for e in explanation:
            st.write(e)

        # Top 3 roles
        vec = vectorizer.transform([" ".join(user_skills)])
        probs = model.predict_proba(vec)[0]
        roles = model.classes_
        top_indices = probs.argsort()[-3:][::-1]

        st.subheader("Top Career Options")
        for i in top_indices:
            st.write(f"{roles[i]} ({round(probs[i]*100,2)}%)")

        st.divider()

        # Skills + Companies
        role_skills = get_role_skills(selected_role)
        companies = get_role_companies(selected_role)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Required Skills")
            st.write(role_skills)

        with col2:
            st.subheader("Top Companies")
            st.write(", ".join(companies))

        # Skill Gap
        matched = [s for s in role_skills if s in user_skills]
        missing = [s for s in role_skills if s not in user_skills]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Skills You Have")
            for s in matched:
                st.write(s)

        with col2:
            st.subheader("Skills Missing")
            for s in missing:
                st.write(s)

        # Chart
        st.subheader("Skill Gap Visualization")

        fig = go.Figure(data=[go.Pie(
            labels=["Matched Skills", "Missing Skills"],
            values=[len(matched), len(missing)],
            hole=0.5
        )])

        st.plotly_chart(fig, use_container_width=True)

        # Readiness
        score = (len(matched) / len(role_skills)) * 100 if role_skills else 0

        st.subheader("Career Readiness")
        st.progress(int(score))
        st.write(f"{round(score,2)}% Ready")

        if len(missing) > len(matched):
            st.warning("You need more improvement")
        else:
            st.success("You are close to job-ready!")

        # Recommendations
        st.subheader("Skills You Should Learn")

        recommendations = recommend_skills(missing)
        for skill in recommendations:
            st.write(skill)

       

        # Suggested Projects
        st.subheader("Recommended Projects")

        projects = suggest_projects(selected_role)
        for p in projects:
            st.write(p)

        # Roadmap
        st.subheader("Career Roadmap")

        roadmap = generate_roadmap(selected_role, missing)
        for step in roadmap:
            st.write(step)