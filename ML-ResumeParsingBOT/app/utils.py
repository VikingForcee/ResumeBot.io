import os
import re
import pdfplumber
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# ==== TEXT EXTRACTION ====

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        # Using .clean_text() can help with some formatting issues
        return "\n".join([page.extract_text(keep_empty_lines=False) or "" for page in pdf.pages])

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# ==== BASIC INFO ====

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text) # More specific email regex
    return match.group(0) if match else ""

def extract_phone(text):
    # Enhanced patterns for various international formats, including Indian numbers
    patterns = [
        r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?', # General international/US
        r'(\+91[\-\s]?)?[6789]\d{9}', # Indian mobile numbers
        r'\b\d{5}[-.\s]?\d{5}\b' # Common 10-digit without country code (e.g., 12345 67890)
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Clean up the phone number, remove spaces/dashes
            return re.sub(r'[^\d+]', '', match.group(0))
    return ""

def extract_name(text):
    # Use spaCy for better name entity recognition
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Heuristic: Often the first PERSON entity in the first few lines is the name.
            # Filter out short names or common single words.
            if len(ent.text.split()) > 1 and len(ent.text.split()) <= 4 and not re.search(r'\d', ent.text):
                return ent.text.strip()
    # Fallback to previous logic if spaCy doesn't find a good name
    for line in text.strip().split('\n')[:5]:
        if line and not re.search(r'@|resume|cv|skills|experience|education|projects', line.lower()):
            if 1 < len(line.split()) <= 4: # Name usually 2-4 words
                return line.strip()
    return ""

# ==== SOCIAL LINKS ====

def has_github(text):
    return bool(re.search(r'github\.com/[\w\-\.]+', text.lower())) # More specific for usernames

def has_linkedin(text):
    return bool(re.search(r'linkedin\.com/in/[\w\-\.]+', text.lower())) # More specific for profile URLs

# ==== SECTION EXTRACTION ====

# More robust section extraction using common headers and looking for patterns
def extract_section(text, keywords, next_section_keywords=[]):
    text_lower = text.lower()
    start_index = -1
    for kw in keywords:
        # Search for the keyword as a whole word or followed by non-alphanumeric
        match = re.search(r'\b' + re.escape(kw.lower()) + r'\b[^a-z]*\n', text_lower)
        if match:
            start_index = match.end()
            break

    if start_index == -1:
        return "" # Changed from "NULL" to "" for consistency

    # Define common section headers that would mark the end of the current section
    # You can expand this list based on common resume formats
    common_end_keywords = [
        "experience", "work experience", "professional experience",
        "education", "academic background",
        "projects", "academic projects", "personal projects",
        "skills", "technical skills", "programming languages", "tool and technologies",
        "achievements", "accomplishments", "awards", "honors",
        "certifications", "licenses", "training",
        "publications", "research",
        "volunteer", "volunteering", "extracurricular activities",
        "interests", "hobbies",
        "summary", "objective", "about me"
    ]
    # Combine with any specific next_section_keywords provided
    all_end_keywords = [re.escape(kw.lower()) for kw in (common_end_keywords + next_section_keywords)]
    end_pattern = r'(\n[ \t]*(' + '|'.join(all_end_keywords) + r')[ \t]*\n)' # Look for header followed by newline

    section_text = text[start_index:]
    end_match = re.search(end_pattern, section_text.lower())

    if end_match:
        end_index = end_match.start()
        section_content = section_text[:end_index].strip()
    else:
        section_content = section_text.strip()

    return ' | '.join([line.strip() for line in section_content.split('\n') if line.strip()])


def extract_experience_details(text):
    # Pass common section keywords as next_section_keywords to help bound the section
    experience_section = extract_section(text, ["EXPERIENCE", "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE"],
                                        next_section_keywords=["EDUCATION", "PROJECTS", "SKILLS"])

    if not experience_section:
        return "", 0, "" # Return empty string, 0 years, empty roles if no experience section

    # Extract total years of experience
    total_years = 0
    # Search for common phrases like "X years of experience"
    years_match = re.search(r'(\d+(\.\d+)?)\s*years?\s*of\s*experience', text.lower())
    if years_match:
        total_years = float(years_match.group(1))
    else:
        # Attempt to sum up durations if explicit total years not found
        durations = re.findall(r'(?:(\d+)\s*years?|(\d+)\s*months?)', experience_section.lower())
        temp_years = 0
        for year, month in durations:
            if year:
                temp_years += int(year)
            if month:
                temp_years += int(month) / 12
        total_years = temp_years

    # Extract job titles
    # A simple approach: Look for lines that might be job titles (often bold, or followed by dates/company)
    # This is a heuristic and may need refinement.
    job_titles = []
    lines = experience_section.split(' | ') # Split by the ' | ' delimiter used in extract_section
    for line in lines:
        # Look for common patterns of a job title: typically capitalized, not too long
        # and potentially followed by date ranges or location
        if re.search(r'\b(manager|engineer|developer|analyst|specialist|lead|architect|director)\b', line.lower()) and \
           len(line.split()) < 10 and line.strip() == line.strip().title(): # Simple title case check
            job_titles.append(line.strip())

    return experience_section, round(total_years, 1), ' | '.join(list(set(job_titles))) # Return unique titles


def extract_education(text):
    section = extract_section(text, ["EDUCATION", "ACADEMIC BACKGROUND"],
                                next_section_keywords=["EXPERIENCE", "SKILLS", "PROJECTS"])
    score = 0
    # Enhanced GPA/Percentage extraction (e.g., 9.5/10, 95%, 3.8/4.0)
    gpa_match = re.search(r'(\d(?:\.\d{1,2})?)\s*(?:/|\s*out\s*of)\s*(?:10(?:\.0)?|4(?:\.0)?)', section)
    percent_match = re.search(r'(\d{2,3}(?:\.\d{1,2})?)\s*%', section)
    cgpa_match = re.search(r'CGPA[:\s]*(\d(?:\.\d{1,2})?)', section)


    if gpa_match:
        gpa_val = float(gpa_match.group(1))
        if '/10' in gpa_match.group(0): # If out of 10, normalize to 100
            gpa_val *= 10
        elif '/4' in gpa_match.group(0): # If out of 4, normalize to 100
            gpa_val *= 25
        score = 5 if gpa_val >= 90 else 3 if gpa_val >= 80 else 2 if gpa_val >= 70 else 1
    elif percent_match:
        p = float(percent_match.group(1))
        score = 5 if p >= 90 else 3 if p >= 80 else 2 if p >= 70 else 1
    elif cgpa_match:
        cgpa_val = float(cgpa_match.group(1))
        # Assuming typical Indian CGPA where max is 10
        cgpa_val_normalized = cgpa_val * 10
        score = 5 if cgpa_val_normalized >= 90 else 3 if cgpa_val_normalized >= 80 else 2 if cgpa_val_normalized >= 70 else 1

    return section, score # No 'or 1' as discussed earlier


def extract_projects(text):
    return extract_section(text, ["PROJECTS", "PROJECT EXPERIENCE", "ACADEMIC PROJECTS", "PERSONAL PROJECTS"],
                           next_section_keywords=["SKILLS", "EXPERIENCE", "EDUCATION", "ACHIEVEMENTS"])

# ==== SKILLS ====

def extract_skills(text):
    # Use spaCy for more dynamic skill extraction
    doc = nlp(text.lower())
    tech_skills = []
    soft_skills = []

    # Predefined lists (can be expanded)
    tech_keywords_base = ["python", "java", "c++", "sql", "html", "css", "javascript", "react", "angular", "node.js",
                          "express.js", "django", "flask", "spring boot", "machine learning", "deep learning",
                          "tensorflow", "pytorch", "keras", "scikit-learn", "numpy", "pandas", "matplotlib", "seaborn",
                          "aws", "azure", "google cloud", "docker", "kubernetes", "git", "linux", "unix",
                          "rest api", "graphql", "mongodb", "postgresql", "mysql", "data science", "big data", "hadoop", "spark"]

    soft_keywords_base = ["communication", "teamwork", "leadership", "problem solving", "adaptability",
                          "critical thinking", "creativity", "collaboration", "time management", "decision making",
                          "interpersonal skills", "presentation skills", "negotiation"]

    # Combine text from skill-like sections
    skills_section = extract_section(text, ["SKILLS", "TECHNICAL SKILLS", "PROGRAMMING LANGUAGES", "TOOLS", "TECHNOLOGIES", "COMPETENCIES"])
    text_to_analyze = (text + " " + skills_section).lower()

    # Regex for finding skills: exact word match or common tech phrases
    for skill in tech_keywords_base:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_to_analyze):
            tech_skills.append(skill.capitalize()) # Capitalize for consistency

    # Look for common soft skill indicators
    for skill in soft_keywords_base:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_to_analyze):
            soft_skills.append(skill.capitalize())

    # Further extraction using noun chunks for potential skills (less precise but more dynamic)
    # This might pick up more noise but also more unlisted skills.
    # Consider adjusting based on desired precision/recall.
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        # Add a heuristic to only consider longer, more specific noun chunks as potential skills
        if len(chunk_text.split()) < 4 and len(chunk_text) > 3 and not re.search(r'\d', chunk_text):
            if any(tech_kw in chunk_text for tech_kw in tech_keywords_base) and chunk_text not in [s.lower() for s in tech_skills]:
                tech_skills.append(chunk_text.capitalize())
            elif any(soft_kw in chunk_text for soft_kw in soft_keywords_base) and chunk_text not in [s.lower() for s in soft_skills]:
                soft_skills.append(chunk_text.capitalize())

    # Remove duplicates and ensure clean list
    tech_skills = sorted(list(set(tech_skills)))
    soft_skills = sorted(list(set(soft_skills)))

    return tech_skills, soft_skills

# ==== TF-IDF Match ====

def compute_tfidf_match(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    # Handle cases where one of the texts might be empty after processing
    if not resume_text or not jd_text:
        return 0.0, 0

    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = (tfidf_matrix[0] @ tfidf_matrix[1].T).toarray()[0][0] * 100

    # More granular JD points based on score
    if score >= 30: # Increased threshold for higher points
        jd_points = 15
    elif score >= 20:
        jd_points = 10
    elif score >= 10:
        jd_points = 5
    elif score >= 5:
        jd_points = 3
    else:
        jd_points = 0
    return score, jd_points