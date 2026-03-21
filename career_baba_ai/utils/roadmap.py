def generate_roadmap(role, missing_skills, time="3-6 months"):

    roadmap = []

    # ---------------- TIME BASED PLAN ----------------
    if time == "1-2 months":
        roadmap.append("Step 1: Learn basic concepts quickly")
        roadmap.append("Step 2: Focus on 1-2 important skills")
        roadmap.append("Step 3: Build 1 small project")
        roadmap.append("Step 4: Revise and practice")

    elif time == "3-6 months":
        roadmap.append("Step 1: Build strong fundamentals")
        roadmap.append("Step 2: Learn core skills deeply")
        roadmap.append("Step 3: Build 2-3 real-world projects")
        roadmap.append("Step 4: Start applying for internships/jobs")

    else:
        roadmap.append("Step 1: Master core concepts")
        roadmap.append("Step 2: Learn advanced topics")
        roadmap.append("Step 3: Build industry-level projects")
        roadmap.append("Step 4: Prepare for interviews")

    # ---------------- SKILL BASED ADDITION ----------------
    for skill in missing_skills[:3]:
        roadmap.append(f"Step {len(roadmap)+1}: Learn {skill}")

    # ---------------- ROLE BASED CUSTOMIZATION ----------------
    if "Data" in role or "AI" in role:
        roadmap.append(f"Step {len(roadmap)+1}: Work on ML/AI projects")
        roadmap.append(f"Step {len(roadmap)+1}: Practice data analysis")

    elif "Frontend" in role:
        roadmap.append(f"Step {len(roadmap)+1}: Build UI projects using React")
        roadmap.append(f"Step {len(roadmap)+1}: Improve UI/UX skills")

    elif "Backend" in role:
        roadmap.append(f"Step {len(roadmap)+1}: Build APIs and backend systems")
        roadmap.append(f"Step {len(roadmap)+1}: Learn databases deeply")

    elif "DevOps" in role or "Cloud" in role:
        roadmap.append(f"Step {len(roadmap)+1}: Practice deployments")
        roadmap.append(f"Step {len(roadmap)+1}: Learn cloud services")

    elif "Cyber" in role:
        roadmap.append(f"Step {len(roadmap)+1}: Practice security tools")
        roadmap.append(f"Step {len(roadmap)+1}: Learn ethical hacking")

    # ---------------- FINAL STEP ----------------
    roadmap.append(f"Step {len(roadmap)+1}: Prepare resume and apply for {role} roles")

    return roadmap