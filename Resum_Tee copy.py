import streamlit as st
from xhtml2pdf import pisa
from pymongo import MongoClient
from io import BytesIO
from content import html_content
import time
from openai import OpenAI

# Define a rate limit (e.g., 10 seconds)
RATE_LIMIT_SECONDS = 10

def create_pdf_from_html(html_content):
    # Create a BytesIO object to store the PDF
    pdf_bytes = BytesIO()

    # Convert HTML to PDF using pisa
    pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_bytes)
    pdf_bytes.seek(0)  # Rewind the BytesIO object for reading

    # Check for pisa status
    if pisa_status.err:
        return None  # Handle error

    return pdf_bytes


def get_resume_drom_jobPost_PerosnalInfo(job_posting):
    # get all personal info from job posting
    perInfo = ""

    # Iterate through the profile sections and concatenate the information
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
    
    print(f"""
          Details: {perInfo}
            Job Posting: {job_posting}
          """)

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

def add_skill():
    skill = st.text_input("Enter skill:")
    details = st.text_area("Skill details:")
    if st.button("Add Skill"):
        st.session_state.profile["skills"].append({"skill": skill, "details": details})
        st.success("Skill added successfully.")

def add_project():
    project_name = st.text_input("Enter project name:")
    project_details = st.text_area("Project details:")
    if st.button("Add Project"):
        st.session_state.profile["projects"].append({"name": project_name, "details": project_details})
        st.success("Project added successfully.")

def add_work_experience():
    job_title = st.text_input("Enter job title:")
    company = st.text_input("Enter company name:")
    experience_details = st.text_area("Experience details:")
    if st.button("Add Work Experience"):
        st.session_state.profile["work_experience"].append({
            "job_title": job_title,
            "company": company,
            "details": experience_details
        })
        st.success("Work Experience added successfully.")

def add_education():
    school = st.text_input("Enter school name:")
    degree = st.text_input("Enter degree:")
    education_details = st.text_area("Education details:")
    if st.button("Add Education"):
        st.session_state.profile["education"].append({
            "school": school,
            "degree": degree,
            "details": education_details
        })
        st.success("Education added successfully.")

def show_profile():
    st.header("Profile")
    
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


MONGO_URI = st.secrets["mongo_uri"]
client = MongoClient(MONGO_URI)
db = client["resum_tee"]

st.set_page_config(page_title="Resum_Tee", page_icon="📄", layout="wide", initial_sidebar_state="expanded")
if 'profile' not in st.session_state:
    st.session_state.profile = {
        "skills": [],
        "projects": [],
        "work_experience": [],
        "education": []
    }
# Initialize rate limit in session state
if "last_request_time" not in st.session_state:
    st.session_state["last_request_time"] = 0
    
if 'resume_html' not in st.session_state:
    st.session_state["resume_html"] = None

with st.sidebar:
    "## Resum_Tee"
    "### Copy the Job Posting :red[(CONTENT Not Link)] and paste it in the text area below"
    ":gray[LinkedIn Doesn't allow scraping, so you have to paste the content here]"
    jobpoasting = st.text_area(
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
            st.session_state["resume_html"] = get_resume_drom_jobPost_PerosnalInfo(jobpoasting)
            pass

tab1, tab2 = st.tabs(["Create Resume", "Create Profile"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True, height=500):
            st.markdown("Job Details")
        
        with st.container(border=True, height=300):
            st.markdown("Match Score")
            
    with col2:
        st.button("Regenerate Resume", use_container_width=True)
        with st.expander("Resume Code"):
            st.code(st.session_state["resume_html"], language="html")
        
        # Display the HTML content in the app
        with st.container(height=630):
            
            if not st.session_state["resume_html"]:
                st.warning("No resume content to display.")
            else:
                st.html(st.session_state["resume_html"])

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
    "Create Profile"
    # Creat a place to make show and edit profile, 
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        with st.expander("Add Skill"):
            add_skill()
    with col2:
        with st.expander("Add Project"):
            add_project()
            
    with col3:
        with st.expander("Add Work Experience"):
            add_work_experience()
    
    with col4:
        with st.expander("Add Education"):
           add_education()
           
           
    show_profile()
    
