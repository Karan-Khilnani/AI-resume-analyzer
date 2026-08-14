import re
import os
import tempfile
from collections import Counter

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader


app = FastAPI(
    title="AI Resume Analyzer & Job Recommendation System",
    version="2.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# JOB DATABASE
# =========================================================

JOBS = [
    {
        "id": 1,
        "title": "Python Backend Developer",
        "company": "TechNova",
        "location": "Remote",
        "skills": [
            "Python",
            "Django",
            "REST API",
            "PostgreSQL",
            "Git"
        ],
        "description":
            "Build scalable backend applications using Python, Django and PostgreSQL."
    },

    {
        "id": 2,
        "title": "Full Stack Developer",
        "company": "CodeCraft",
        "location": "Bangalore",
        "skills": [
            "Python",
            "React",
            "JavaScript",
            "PostgreSQL",
            "REST API"
        ],
        "description":
            "Develop full-stack web applications using modern frontend and backend technologies."
    },

    {
        "id": 3,
        "title": "Frontend Developer",
        "company": "PixelLabs",
        "location": "Remote",
        "skills": [
            "JavaScript",
            "TypeScript",
            "React",
            "Vue",
            "Tailwind CSS"
        ],
        "description":
            "Create responsive and modern web interfaces."
    },

    {
        "id": 4,
        "title": "Django Developer",
        "company": "CloudWorks",
        "location": "Hyderabad",
        "skills": [
            "Python",
            "Django",
            "Django REST Framework",
            "PostgreSQL",
            "Docker"
        ],
        "description":
            "Develop REST APIs and backend services using Django."
    },

    {
        "id": 5,
        "title": "Software Engineer",
        "company": "InnovateTech",
        "location": "Pune",
        "skills": [
            "Python",
            "Java",
            "SQL",
            "Git",
            "Docker"
        ],
        "description":
            "Work on scalable software systems and cloud-based applications."
    },

    {
        "id": 6,
        "title": "DevOps Engineer",
        "company": "CloudScale",
        "location": "Bangalore",
        "skills": [
            "AWS",
            "Docker",
            "Kubernetes",
            "Linux",
            "CI/CD",
            "Git"
        ],
        "description":
            "Manage cloud infrastructure, deployment pipelines and containerized applications."
    },

    {
        "id": 7,
        "title": "Data Analyst",
        "company": "DataWorks",
        "location": "Mumbai",
        "skills": [
            "Python",
            "SQL",
            "Excel",
            "Data Science",
            "Machine Learning"
        ],
        "description":
            "Analyze datasets and create data-driven insights for business decisions."
    }
]


# =========================================================
# SKILLS
# =========================================================

SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C",
    "SQL",
    "HTML",
    "CSS",

    "React",
    "Vue",
    "Vue.js",
    "Nuxt",
    "Nuxt.js",
    "Angular",
    "Tailwind CSS",

    "Django",
    "Django REST Framework",
    "REST API",
    "REST APIs",
    "Flask",
    "FastAPI",

    "Node.js",
    "Express",

    "PostgreSQL",
    "MySQL",
    "MongoDB",

    "Git",
    "GitHub",
    "Bitbucket",

    "Docker",
    "Kubernetes",

    "AWS",
    "AWS EC2",
    "Azure",
    "GCP",

    "Linux",
    "CI/CD",
    "Jenkins",

    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "Data Science",

    "Figma",
    "Excel"
]


# =========================================================
# SECTION DETECTION
# =========================================================

SECTION_KEYWORDS = {

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship"
    ],

    "education": [
        "education",
        "academic",
        "qualification",
        "university",
        "college"
    ],

    "projects": [
        "projects",
        "project"
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "technical expertise"
    ],

    "summary": [
        "summary",
        "profile",
        "objective",
        "about me"
    ]
}


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = text.replace("\x00", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# =========================================================
# EMAIL
# =========================================================

def detect_email(text):

    return bool(
        re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )
    )


# =========================================================
# PHONE
# =========================================================

def detect_phone(text):

    patterns = [
        r"\+91[\s-]?[6-9]\d{9}",
        r"\b[6-9]\d{9}\b",
        r"\(\d{3}\)[\s-]\d{3}[\s-]\d{4}"
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


# =========================================================
# NAME
# =========================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "Candidate"

    ignored = [
        "resume",
        "curriculum vitae",
        "cv"
    ]

    for line in lines[:8]:

        lower = line.lower()

        if lower in ignored:
            continue

        if "@" in line:
            continue

        if re.search(r"\d", line):
            continue

        if 2 <= len(line.split()) <= 5:
            return line

    return "Candidate"


# =========================================================
# SKILL DETECTION
# =========================================================

def detect_skills(text):

    text_lower = text.lower()

    detected = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(
            skill.lower()
        ) + r"(?!\w)"

        if re.search(pattern, text_lower):

            if skill not in detected:
                detected.append(skill)

    return detected


# =========================================================
# SECTION DETECTION
# =========================================================

def detect_sections(text):

    text_lower = text.lower()

    sections = {}

    for section, keywords in SECTION_KEYWORDS.items():

        sections[section] = any(
            keyword.lower() in text_lower
            for keyword in keywords
        )

    return sections


# =========================================================
# ACHIEVEMENT DETECTION
# =========================================================

def detect_achievements(text):

    achievement_patterns = [

        r"\b\d+%\b",

        r"\b\d+\+?\s*(users|customers|clients)\b",

        r"\b\d+\+?\s*(projects|applications)\b",

        r"\b(increased|improved|reduced|optimized|saved|grew)\b",

        r"\b(awarded|winner|won|ranked|achievement)\b",

        r"\b(top \d+)\b"

    ]

    matches = 0

    for pattern in achievement_patterns:

        matches += len(
            re.findall(
                pattern,
                text,
                re.IGNORECASE
            )
        )

    return matches


# =========================================================
# ATS STRUCTURE SCORE
# =========================================================

def calculate_ats_score(
    text,
    sections,
    email,
    phone
):

    score = 0

    reasons = []

    # Contact
    if email:
        score += 5
    else:
        reasons.append(
            "Add a professional email address."
        )

    if phone:
        score += 5
    else:
        reasons.append(
            "Add a phone number."
        )

    # Sections
    important_sections = [
        "experience",
        "education",
        "projects",
        "skills"
    ]

    section_points = 20

    found_sections = sum(
        sections.get(section, False)
        for section in important_sections
    )

    score += round(
        found_sections
        / len(important_sections)
        * section_points
    )

    # Length
    word_count = len(text.split())

    if 250 <= word_count <= 900:

        score += 15

    elif 150 <= word_count < 250:

        score += 10

        reasons.append(
            "Resume could contain more detailed information."
        )

    else:

        score += 5

        reasons.append(
            "Resume length could be improved."
        )

    # Formatting indicators
    if "\n" in text:

        score += 5

    return min(score, 50), reasons


# =========================================================
# SKILL SCORE
# =========================================================

def calculate_skill_score(skills):

    if len(skills) >= 12:
        return 20

    if len(skills) >= 9:
        return 18

    if len(skills) >= 7:
        return 15

    if len(skills) >= 5:
        return 12

    if len(skills) >= 3:
        return 8

    return 4


# =========================================================
# EXPERIENCE SCORE
# =========================================================

def calculate_experience_score(
    text,
    sections
):

    if not sections["experience"]:
        return 0

    score = 8

    text_lower = text.lower()

    action_verbs = [
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "optimized",
        "managed",
        "led",
        "deployed",
        "automated"
    ]

    action_count = sum(
        text_lower.count(verb)
        for verb in action_verbs
    )

    if action_count >= 5:
        score += 5

    elif action_count >= 2:
        score += 3

    return min(score, 15)


# =========================================================
# PROJECT SCORE
# =========================================================

def calculate_project_score(
    text,
    sections
):

    if not sections["projects"]:
        return 0

    score = 8

    text_lower = text.lower()

    project_indicators = [
        "github",
        "deployed",
        "api",
        "database",
        "frontend",
        "backend",
        "framework"
    ]

    indicator_count = sum(
        text_lower.count(item)
        for item in project_indicators
    )

    if indicator_count >= 5:
        score += 7

    elif indicator_count >= 2:
        score += 4

    return min(score, 15)


# =========================================================
# EDUCATION SCORE
# =========================================================

def calculate_education_score(sections):

    if sections["education"]:
        return 10

    return 0


# =========================================================
# ACHIEVEMENT SCORE
# =========================================================

def calculate_achievement_score(
    achievement_count
):

    if achievement_count >= 5:
        return 10

    if achievement_count >= 3:
        return 8

    if achievement_count >= 1:
        return 5

    return 0


# =========================================================
# KEYWORD SCORE
# =========================================================

def calculate_keyword_score(
    text,
    skills
):

    text_lower = text.lower()

    keyword_groups = [

        ["develop", "built", "implemented"],

        ["api", "rest"],

        ["database", "sql"],

        ["software", "application"],

        ["testing", "debugging"],

        ["deployment", "deploy"],

    ]

    found = 0

    for group in keyword_groups:

        if any(
            word in text_lower
            for word in group
        ):

            found += 1

    skill_bonus = min(
        len(skills),
        4
    )

    return min(
        10,
        round(
            found / len(keyword_groups) * 6
        ) + skill_bonus
    )


# =========================================================
# MAIN ANALYSIS
# =========================================================

def analyze_resume(text):

    text = clean_text(text)

    skills = detect_skills(text)

    sections = detect_sections(text)

    email = detect_email(text)

    phone = detect_phone(text)

    achievements = detect_achievements(text)

    name = extract_name(text)

    # Individual scores

    ats_structure, ats_reasons = calculate_ats_score(
        text,
        sections,
        email,
        phone
    )

    # Normalize ATS component to 15
    ats_component = round(
        ats_structure / 50 * 15
    )

    skill_component = calculate_skill_score(
        skills
    )

    experience_component = calculate_experience_score(
        text,
        sections
    )

    project_component = calculate_project_score(
        text,
        sections
    )

    education_component = calculate_education_score(
        sections
    )

    achievement_component = calculate_achievement_score(
        achievements
    )

    keyword_component = calculate_keyword_score(
        text,
        skills
    )

    contact_component = 5 if (
        email and phone
    ) else (
        3 if email or phone else 0
    )

    # Final score

    overall_score = (
        ats_component
        + skill_component
        + experience_component
        + project_component
        + education_component
        + achievement_component
        + keyword_component
        + contact_component
    )

    overall_score = min(
        100,
        overall_score
    )

    # -----------------------------------------------------
    # Strengths
    # -----------------------------------------------------

    strengths = []

    if len(skills) >= 7:
        strengths.append(
            f"Strong technical skill coverage with {len(skills)} detected skills."
        )

    elif len(skills) >= 4:
        strengths.append(
            "Good technical skill coverage."
        )

    if sections["projects"]:
        strengths.append(
            "Projects provide evidence of practical experience."
        )

    if sections["experience"]:
        strengths.append(
            "Professional experience is clearly represented."
        )

    if achievements >= 2:
        strengths.append(
            "Resume contains measurable achievements or impact indicators."
        )

    if email and phone:
        strengths.append(
            "Contact information is complete."
        )

    if sections["education"]:
        strengths.append(
            "Educational background is clearly structured."
        )

    if not strengths:
        strengths.append(
            "Resume contains relevant professional information."
        )

    # -----------------------------------------------------
    # Weaknesses
    # -----------------------------------------------------

    weaknesses = []

    weaknesses.extend(
        ats_reasons
    )

    if len(skills) < 5:
        weaknesses.append(
            "Increase the number of relevant technical skills."
        )

    if not sections["projects"]:
        weaknesses.append(
            "Add 2–3 relevant projects with technologies and outcomes."
        )

    if not sections["experience"]:
        weaknesses.append(
            "Add internship, work experience or relevant practical experience."
        )

    if achievements == 0:
        weaknesses.append(
            "Add measurable results such as percentages, users, performance improvements or rankings."
        )

    if not sections["certifications"]:
        weaknesses.append(
            "Relevant certifications can strengthen the profile."
        )

    # Remove duplicates
    weaknesses = list(
        dict.fromkeys(weaknesses)
    )

    # -----------------------------------------------------
    # Missing common skills
    # -----------------------------------------------------

    common_skills = [
        "Git",
        "REST API",
        "Docker",
        "AWS",
        "PostgreSQL"
    ]

    skill_set = {
        skill.lower()
        for skill in skills
    }

    missing_skills = [
        skill
        for skill in common_skills
        if skill.lower() not in skill_set
    ]

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    summary = (
        f"{name} has a resume score of {overall_score}/100 "
        f"with {len(skills)} technical skills detected. "
    )

    if sections["experience"]:
        summary += (
            "Professional experience is present. "
        )

    if sections["projects"]:
        summary += (
            "The resume also demonstrates practical project work. "
        )

    if achievements:
        summary += (
            f"{achievements} measurable achievement indicators were detected. "
        )

    summary += (
        "The biggest improvement opportunity is to tailor the resume "
        "toward specific job requirements and quantify professional impact."
    )

    return {
        "candidate_name": name,

        "summary": summary,

        "overall_score": overall_score,

        "skills": skills,

        "technical_skills": skills,

        "soft_skills": [],

        "experience": [],

        "education": [],

        "projects": [],

        "strengths": strengths,

        "weaknesses": weaknesses,

        "missing_skills": missing_skills,

        "suggestions": [
            "Tailor keywords to the target job description.",
            "Use measurable achievements wherever possible.",
            "Describe projects using action + technology + result.",
            "Keep formatting clean and ATS-friendly.",
            "Prioritize skills that appear in the target job description."
        ],

        "score_breakdown": {
            "ATS Structure": ats_component,
            "Skills": skill_component,
            "Experience": experience_component,
            "Projects": project_component,
            "Education": education_component,
            "Achievements": achievement_component,
            "Keywords": keyword_component,
            "Contact": contact_component
        }
    }


# =========================================================
# JOB MATCHING
# =========================================================

def calculate_job_match(
    resume_skills,
    resume_text,
    job
):

    resume_skill_set = {
        skill.lower()
        for skill in resume_skills
    }

    job_skill_set = {
        skill.lower()
        for skill in job["skills"]
    }

    matched = (
        resume_skill_set
        & job_skill_set
    )

    missing = (
        job_skill_set
        - resume_skill_set
    )

    # Skill match
    if job_skill_set:

        skill_match = (
            len(matched)
            / len(job_skill_set)
        ) * 100

    else:

        skill_match = 0


    # Keyword relevance
    job_text = (
        job["title"]
        + " "
        + job["description"]
        + " "
        + " ".join(job["skills"])
    ).lower()

    resume_text_lower = resume_text.lower()

    job_words = set(
        re.findall(
            r"\b[a-zA-Z][a-zA-Z+#.]+\b",
            job_text
        )
    )

    resume_words = set(
        re.findall(
            r"\b[a-zA-Z][a-zA-Z+#.]+\b",
            resume_text_lower
        )
    )

    keyword_overlap = len(
        job_words & resume_words
    )

    keyword_match = min(
        100,
        keyword_overlap * 5
    )


    # Title relevance
    title_words = set(
        re.findall(
            r"\b[a-zA-Z]+\b",
            job["title"].lower()
        )
    )

    title_overlap = len(
        title_words & resume_words
    )

    title_match = min(
        100,
        title_overlap * 30
    )


    # Final weighted score
    final_score = round(
        skill_match * 0.60
        + keyword_match * 0.25
        + title_match * 0.15
    )

    final_score = min(
        100,
        final_score
    )

    return {
        **job,

        "match_score": final_score,

        "matched_skills": sorted(
            list(matched)
        ),

        "missing_skills": sorted(
            list(missing)
        )
    }


# =========================================================
# ANALYZE ENDPOINT
# =========================================================

@app.post("/api/analyze-resume")
async def analyze_resume_endpoint(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume."
        )

    contents = await file.read()

    temp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as f:

            f.write(contents)

            temp_file = f.name

        # Extract
        resume_text = extract_pdf_text(
            temp_file
        )

        if not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from this PDF. "
                    "Please upload a text-based PDF."
                )
            )

        # Analyze
        analysis = analyze_resume(
            resume_text
        )

        resume_skills = (
            analysis["skills"]
        )

        # Match jobs
        recommendations = []

        for job in JOBS:

            recommendation = calculate_job_match(
                resume_skills,
                resume_text,
                job
            )

            recommendations.append(
                recommendation
            )

        recommendations.sort(
            key=lambda job: job["match_score"],
            reverse=True
        )

        return {
            "success": True,

            "filename": file.filename,

            "analysis": analysis,

            "recommendations": recommendations
        }

    finally:

        if (
            temp_file
            and os.path.exists(temp_file)
        ):

            os.remove(temp_file)


# =========================================================
# JOBS ENDPOINT
# =========================================================

@app.get("/api/jobs")
def get_jobs():

    return {
        "success": True,
        "jobs": JOBS
    }