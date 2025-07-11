import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from app.utils import *

def compute_tfidf_match(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    return (tfidf_matrix[0] @ tfidf_matrix[1].T).toarray()[0][0] * 100

def run_resume_parser(jd_text, resume_folder, output_file="parsed.csv"):
    if not jd_text:
        raise ValueError("JD text must be provided!")

    rows = []

    for file in os.listdir(resume_folder):
        if file.endswith((".pdf", ".docx")):
            path = os.path.join(resume_folder, file)
            text = extract_text_from_pdf(path) if file.endswith(".pdf") else extract_text_from_docx(path)
            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            tfidf = compute_tfidf_match(text, jd_text)
            status = "Shortlisted" if tfidf > 15 else ("To be Reviewed" if tfidf > 8 else "Rejected")

            rows.append({
                "Filename": file,
                "Name": name,
                "Email": email,
                "Phone": phone,
                "JD_Match_Score": round(tfidf, 2),
                "Status": status
            })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")
