import streamlit as st
import os
import pandas as pd
from app.parser import parse_resumes_with_jd
from app.utils import extract_text_from_pdf, extract_text_from_docx
from app.emailer import send_email


st.set_page_config(page_title="Resume Parser", layout="wide")
st.title("📄 Resume Parser & JD Analyzer")
st.markdown("Upload a Job Description and Resumes to extract structured info and shortlist candidates.")

# === Upload JD ===
jd_file = st.file_uploader("📥 Upload Job Description File (TXT / PDF / DOCX)", type=["txt", "pdf", "docx"])

# === Upload Resumes ===
resumes = st.file_uploader("📥 Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

if jd_file and resumes:
    if st.button("🚀 Parse Resumes"):
        os.makedirs("tmp", exist_ok=True)

        # === Process JD file ===
        jd_ext = jd_file.name.split(".")[-1].lower()
        jd_text = ""

        jd_path = os.path.join("tmp", f"jd_tmp.{jd_ext}")
        with open(jd_path, "wb") as f:
            f.write(jd_file.read())

        # Extract JD text based on file type
        if jd_ext == "pdf":
            jd_text = extract_text_from_pdf(jd_path)
        elif jd_ext == "docx":
            jd_text = extract_text_from_docx(jd_path)
        elif jd_ext == "txt":
            with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
                jd_text = f.read()
        else:
            st.error("Unsupported JD file type.")
            st.stop()

        # === Save Resumes ===
        resume_folder = "tmp/resumes"
        os.makedirs(resume_folder, exist_ok=True)

        for resume in resumes:
            resume_path = os.path.join(resume_folder, resume.name)
            with open(resume_path, "wb") as f:
                f.write(resume.read())

        # === Run Parser ===
        output_file = "tmp/parsed_resumes.csv"
        df = parse_resumes_with_jd(resume_folder, jd_text, output_file)

        st.session_state['parsed_df'] = df
        st.success("✅ Parsing Complete!")

# === Display Results ===
if 'parsed_df' in st.session_state:
    df = st.session_state['parsed_df']

    st.dataframe(df)
    st.download_button(
        label="⬇️ Download Results as CSV", # Using a simpler down arrow emoji
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="parsed_resumes.csv",
        mime="text/csv"
    )


    # === Send Emails ===
    if "Email" in df.columns and "Status" in df.columns:
        st.subheader("Send Emails to Candidates")
        if st.button("Send Emails Now"):
            sent = 0
            for _, row in df.iterrows():
                name = row.get("Name", "Candidate")
                email = row.get("Email", "")
                status = str(row.get("Status", "")).strip()

                if status in ["Shortlisted", "Rejected"] and email:
                    success = send_email(email, name, status)
                    if success:
                        sent += 1
            st.success(f"Emails sent to {sent} candidates.")
    else:
        st.warning("'Email' or 'Status' column not found in parsed data.")
