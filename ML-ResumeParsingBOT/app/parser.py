# parser.py
# Changed imports to be explicit as discussed previously
from app.utils import (
    extract_text_from_pdf, extract_text_from_docx,
    extract_name, extract_email, extract_phone,
    has_github, has_linkedin,
    extract_experience_details, extract_education, extract_projects,
    extract_section, extract_skills, compute_tfidf_match
)
import os
import pandas as pd
import streamlit as st # Keep this for st.info

def parse_resumes_with_jd(folder_path, jd_text, output_file="parsed_resumes_final.csv"):
    resume_data = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.pdf', '.docx')):
            path = os.path.join(folder_path, filename)

            # Extract text
            try: # Added try-except for robust text extraction
                if filename.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(path)
                else:
                    text = extract_text_from_docx(path)
                if not text.strip(): # Skip empty resumes
                    st.warning(f"Skipping empty or unreadable resume: {filename}")
                    continue
            except Exception as e:
                st.error(f"Error extracting text from {filename}: {e}")
                continue


            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            github = has_github(text)
            linkedin = has_linkedin(text)
            experience_section, years_of_experience, job_titles = extract_experience_details(text) # New returns
            education_section, education_score = extract_education(text)
            projects = extract_projects(text)
            achievements = extract_section(text, ["ACHIEVEMENTS", "ACCOMPLISHMENTS", "AWARDS"])
            tech_skills, soft_skills = extract_skills(text)
            tfidf_score, jd_points = compute_tfidf_match(text, jd_text)

            score = 0
            # Base presence points
            score += 10 if name else 0
            score += 10 if email else 0
            score += 10 if phone else 0
            score += 3 if github else 0
            score += 3 if linkedin else 0

            # Education score from function
            score += education_score

            # Experience points - now includes years of experience
            score += 5 if experience_section else 0 # Points for having an experience section
            if years_of_experience >= 5: score += 10 # Senior experience
            elif years_of_experience >= 2: score += 5 # Mid-level experience
            else: score += 2 # Junior experience

            score += 5 if projects else 0
            score += 3 if achievements else 0 # Points for achievements

            # Skill points (adjusted weights)
            score += len(tech_skills) * 3.0 # Tech skills usually more critical
            score += len(soft_skills) * 1.0

            # JD Match points
            score += jd_points

            # Normalize score if it exceeds a certain maximum (optional, but good for consistent scaling)
            # max_possible_score = ... calculate based on max points from all categories
            # score = min(score, max_possible_score) # Cap the score


            if score > 70: # Adjusted thresholds based on new scoring
                status = "Shortlisted"
            elif score > 45:
                status = "To be Reviewed"
            else:
                status = "Rejected"

            resume_data.append({
                'Filename': filename,
                'Name': name,
                'Email': email,
                'Phone': phone,
                'LinkedIn': linkedin,
                'GitHub': github,
                'EducationScore': education_score,
                'Education': education_section,
                'YearsExperience': years_of_experience, # New field
                'JobTitles': ', '.join(job_titles),    # New field
                'TechSkills': ', '.join(tech_skills),
                'SoftSkills': ', '.join(soft_skills),
                'ExperienceDetails': experience_section, # Renamed for clarity
                'Achievements': achievements,
                'Projects': projects,
                'JD_Match_Score': round(tfidf_score, 2),
                'Status': status,
                'Final_Score': round(score, 2)
            })

    df = pd.DataFrame(resume_data)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    st.info(f"✅ Parsing complete. Saved as '{output_file}'.")
    return df