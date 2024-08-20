import streamlit as st
from xhtml2pdf import pisa
from pymongo import MongoClient
from io import BytesIO
import time
import bcrypt
from openai import OpenAI

# Define a rate limit (e.g., 10 seconds)
RATE_LIMIT_SECONDS = 10

# MongoDB connection
MONGO_URI = st.secrets["mongo_uri"]
client = MongoClient(MONGO_URI)
db = client["resum_tee"]
users_collection = db["users"]

# Function to create a PDF from HTML content
def create_pdf_from_html(html_content):
    if not html_content:
        return None
    
    pdf_bytes = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_bytes)
    pdf_bytes.seek(0)
    if pisa_status.err:
        return None
    return pdf_bytes

# Function to generate resume HTML using OpenAI's GPT model
def get_resume_drom_jobPost_PerosnalInfo(job_posting):
    perInfo = ""

    for section, items in st.session_state.profile.items():
        if section == "skills":
            perInfo += "Skills:\n"
            for skill in items:
                perInfo += f"- {skill['skill']}: {skill['details']}\n"
        elif section == "projects":
            perInfo += "Projects:\n"
            for project in items:
                perInfo += f"- {project['name']}: {project['details']}\n"
        elif section == "work_experience":
            perInfo += "Work Experience:\n"
            for experience in items:
                perInfo += f"- {experience['job_title']} at {experience['company']}: {experience['details']}\n"
        elif section == "education":
            perInfo += "Education:\n"
            for education in items:
                perInfo += f"- {education['school']} ({education['degree']}): {education['details']}\n"

    client = OpenAI(api_key=st.secrets["openai_api_key"])
    completion = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {
                'role': 'system',
                'content': 'You are a skilled HTML and CSS developer, who designs beautiful resumes in HTML and CSS only. You only reply in valid HTML and CSS code. Your job is to make the best resume possible for the JOB posting and personal info provided to you.'
            },
            {
                'role': 'user',
                'content': f"""
                You have been provided a Job Posting and info of a candidate. You will design a simple and clean resume in HTML and CSS only.
                You will figure out the keywords important for the Job Posting and mold the resume accordingly.
                You will only use the information provided to you, you will not use any external information.
                ###
                Job Posting:
                {job_posting}
                
                Personal Info:
                {perInfo}
                ###
                
                Here is an example of a simple resume structure:
                ***
                <div style="background-color:#ffffff; padding:20px; border-radius:15px; height:100%; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: 'Arial', sans-serif;">
                <div style="text-align:center; margin-bottom: 30px;">
                    <h1 style="color:#34495e; font-size:36px; margin: 0;">John Doe</h1>
                    <p style="color:#7f8c8d; font-size:18px; margin: 5px 0;">Full Stack Developer</p>
                    <p style="color:#95a5a6; font-size:16px; margin: 5px 0;">john.doe@example.com | +1-234-567-890</p>
                </div>
                
                <div style="border-top: 2px solid #34495e; padding-top: 20px;">
                    <h2 style="color:#34495e; font-size:24px; border-bottom: 2px solid #34495e; display: inline-block; margin-bottom: 10px;">Summary</h2>
                    <p style="color:#2c3e50; font-size:16px; line-height:1.5;">
                        A highly skilled and experienced Full Stack Developer with a passion for creating robust and scalable web applications.
                        Expertise in JavaScript, Python, and modern frameworks. Proven ability to lead teams and deliver high-quality projects on time.
                    </p>
                </div>
                
                <div style="border-top: 2px solid #34495e; padding-top: 20px;">
                    <h2 style="color:#34495e; font-size:24px; border-bottom: 2px solid #34495e; display: inline-block; margin-bottom: 10px;">Experience</h2>
                    <ul style="color:#2c3e50; font-size:16px; line-height:1.8; list-style-type: none; padding-left: 0;">
                        <li><strong>Senior Developer at XYZ Corp</strong> - Jan 2020 to Present</li>
                        <li><strong>Developer at ABC Inc.</strong> - Aug 2017 to Dec 2019</li>
                        <li><strong>Junior Developer at DEF LLC</strong> - Jun 2015 to Jul 2017</li>
                    </ul>
                </div>
                
                <div style="border-top: 2px solid #34495e; padding-top: 20px;">
                    <h2 style="color:#34495e; font-size:24px; border-bottom: 2px solid #34495e; display: inline-block; margin-bottom: 10px;">Skills</h2>
                    <p style="color:#2c3e50; font-size:16px; line-height:1.5;">
                        JavaScript, React, Node.js, Python, Django, Flask, SQL, NoSQL, HTML, CSS, Git, Docker, Kubernetes, AWS
                    </p>
                </div>
                
                <div style="border-top: 2px solid #34495e; padding-top: 20px;">
                    <h2 style="color:#34495e; font-size:24px; border-bottom: 2px solid #34495e; display: inline-block; margin-bottom: 10px;">Education</h2>
                    <ul style="color:#2c3e50; font-size:16px; line-height:1.8; list-style-type: none; padding-left: 0;">
                        <li><strong>Bachelor of Science in Computer Science</strong> - University of Technology, 2015</li>
                    </ul>
                </div>
            </div>
                ***
                USE ONLY The information provided to you between the first and second ###.
                Return only the HTML+CSS code, add nothing else. THIS IS EXTREMELY IMPORTANT.

                """
            }
        ])
    res = completion.choices[0].message.content
    return res

# Functions for handling profile data
def add_skill():
    skill = st.text_input("Enter skill:", key="skill_input")
    details = st.text_area("Skill details:", key="skill_details")
    if st.button("Add Skill", key="add_skill_button"):
        st.session_state.profile["skills"].append({"skill": skill, "details": details})
        st.success("Skill added successfully.")

def add_project():
    project_name = st.text_input("Enter project name:", key="project_name")
    project_details = st.text_area("Project details:", key="project_details")
    if st.button("Add Project", key="add_project_button"):
        st.session_state.profile["projects"].append({"name": project_name, "details": project_details})
        st.success("Project added successfully.")

def add_work_experience():
    job_title = st.text_input("Enter job title:", key="job_title")
    company = st.text_input("Enter company name:", key="company_name")
    experience_details = st.text_area("Experience details:", key="experience_details")
    if st.button("Add Work Experience", key="add_experience_button"):
        st.session_state.profile["work_experience"].append({
            "job_title": job_title,
            "company": company,
            "details": experience_details
        })
        st.success("Work Experience added successfully.")

def add_education():
    school = st.text_input("Enter school name:", key="school_name")
    degree = st.text_input("Enter degree:", key="degree")
    education_details = st.text_area("Education details:", key="education_details")
    if st.button("Add Education", key="add_education_button"):
        st.session_state.profile["education"].append({
            "school": school,
            "degree": degree,
            "details": education_details
        })
        st.success("Education added successfully.")

def show_profile():
    st.header("Profile")
    
    st.subheader("Personal Information")
    st.text(f"Name: {st.session_state.profile['personal_info'].get('name', '')}")
    st.text(f"Email: {st.session_state.profile['personal_info'].get('email', '')}")
    st.text(f"Phone: {st.session_state.profile['personal_info'].get('phone', '')}")
    st.text(f"Location: {st.session_state.profile['personal_info'].get('location', '')}")
    
    st.subheader("Skills")
    for skill in st.session_state.profile["skills"]:
        st.text(f"Skill: {skill['skill']}")
        st.text(f"Details: {skill['details']}")
    
    st.subheader("Projects")
    for project in st.session_state.profile["projects"]:
        st.text(f"Project: {project['name']}")
        st.text(f"Details: {project['details']}")
    
    st.subheader("Work Experience")
    for experience in st.session_state.profile["work_experience"]:
        st.text(f"Job Title: {experience['job_title']}")
        st.text(f"Company: {experience['company']}")
        st.text(f"Details: {experience['details']}")
    
    st.subheader("Education")
    for education in st.session_state.profile["education"]:
        st.text(f"School: {education['school']}")
        st.text(f"Degree: {education['degree']}")
        st.text(f"Details: {education['details']}")

# Authentication functions
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def save_user(username, password):
    hashed_password = hash_password(password)
    users_collection.insert_one({"username": username, "password": hashed_password})

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and check_password(password, user["password"]):
        return user
    return None

def save_profile(username, profile):
    users_collection.update_one({"username": username}, {"$set": {"profile": profile}}, upsert=True)

def load_profile(username):
    user = users_collection.find_one({"username": username})
    return user.get("profile", None)

# App configuration
st.set_page_config(page_title="Resum_Tee", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# App state management
if 'profile' not in st.session_state:
    st.session_state.profile = {
        "personal_info": {},
        "skills": [],
        "projects": [],
        "work_experience": [],
        "education": []
    }

if 'resume_html' not in st.session_state:
    st.session_state["resume_html"] = None

if 'username' not in st.session_state:
    st.session_state["username"] = None

if "last_request_time" not in st.session_state:
    st.session_state["last_request_time"] = 0

def show_logged_in():
    with st.sidebar:
        "## Resum_Tee"
        "### Copy the Job Posting :red[(CONTENT Not Link)] and paste it in the text area below"
        ":gray[LinkedIn Doesn't allow scraping, so you have to paste the content here]"
        jobposting = st.text_area(
            label="Job Posting",
            placeholder="Paste your JOB posting here, NOT LINK",
            height=500)
        
        generate_resume = st.button("Generate Resume", use_container_width=True)

        # Enforce rate limit
        if generate_resume:
            current_time = time.time()
            if current_time - st.session_state["last_request_time"] < RATE_LIMIT_SECONDS:
                st.error(f"Please wait {RATE_LIMIT_SECONDS} seconds between requests.")
            else:
                st.session_state["last_request_time"] = current_time
                st.session_state["resume_html"] = get_resume_drom_jobPost_PerosnalInfo(jobposting)

    tab1, tab2 = st.tabs(["Create Resume", "Create Profile"])

    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("Job Details")
            st.markdown("Match Score")
                
        with col2:
            st.button("Regenerate Resume", use_container_width=True)
            with st.expander("Resume Code"):
                st.code(st.session_state["resume_html"], language="html")
            
            # Display the HTML content in the app
            with st.container():
                if not st.session_state["resume_html"]:
                    st.warning("No resume content to display.")
                else:
                    st.components.v1.html(st.session_state["resume_html"], height=630)

            # Create the PDF from the HTML content
            pdf_data = create_pdf_from_html(st.session_state["resume_html"])

            # Create a download button for the PDF
            if pdf_data:
                st.download_button(
                    label="Download Resume as PDF",
                    data=pdf_data,
                    file_name="resume.pdf",  # Default download filename
                    mime="application/pdf",  # MIME type for PDF files
                    use_container_width=True
                )
            else:
                st.error("Failed to generate PDF")
                
    with tab2:
        st.markdown("## Create Profile")
        # Create a place to show and edit profile
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            with st.expander("Add Personal Information"):
                st.session_state.profile["personal_info"]["name"] = st.text_input("Enter Name", value=st.session_state.profile["personal_info"].get("name", ""))
                st.session_state.profile["personal_info"]["email"] = st.text_input("Enter Email", value=st.session_state.profile["personal_info"].get("email", ""))
                st.session_state.profile["personal_info"]["phone"] = st.text_input("Enter Phone", value=st.session_state.profile["personal_info"].get("phone", ""))
                st.session_state.profile["personal_info"]["location"] = st.text_input("Enter Location", value=st.session_state.profile["personal_info"].get("location", ""))
        
        with col2:
            with st.expander("Add Skill"):
                add_skill()
        with col3:
            with st.expander("Add Project"):
                add_project()
                
        with col4:
            with st.expander("Add Work Experience"):
                add_work_experience()
        
        with st.expander("Add Education"):
            add_education()
        
        show_profile()
        
        if st.button("Save Profile", key="save_profile"):
            save_profile(st.session_state["username"], st.session_state.profile)
            st.success("Profile saved successfully.")

# User authentication
if st.session_state["username"] is None:
    st.sidebar.header("Authentication")
    auth_choice = st.sidebar.radio("Login or Signup", ["Login", "Signup"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if auth_choice == "Signup":
        if st.sidebar.button("Signup"):
            if username and password:
                save_user(username, password)
                st.success("Signup successful! Please login.")
            else:
                st.error("Please provide both username and password.")

    elif auth_choice == "Login":
        if st.sidebar.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["username"] = username
                loaded_profile = load_profile(username)
                if loaded_profile:
                    st.session_state.profile = loaded_profile
                st.success("Login successful!")
                show_logged_in()
            else:
                st.error("Invalid username or password.")
else:
    show_logged_in()
