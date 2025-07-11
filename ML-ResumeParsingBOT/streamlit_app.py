import streamlit as st
import os
import pandas as pd
from app.parser import run_resume_parser
from app.emailer import send_email  # Make sure this is correct

st.set_page_config(page_title="Resume Parser", layout="wide")

st.title("📄 Resume Parser & JD Analyzer")
st.markdown("Upload a Job Description and Resumes to extract structured info and shortlist candidates.")

# === Upload JD ===
jd_file = st.file_uploader("📥 Upload Job Description File (TXT / PDF / DOCX)", type=["txt", "pdf", "docx"])

# === Upload Resumes ===
resumes = st.file_uploader("📥 Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# === Parse Button ===
if jd_file and resumes:
    if st.button("🚀 Parse Resumes"):
        os.makedirs("tmp", exist_ok=True)
        import io
        from app.utils import extract_text_from_pdf, extract_text_from_docx

        # Read JD content as text
        if jd_file.name.endswith(".txt"):
            jd_text = jd_file.read().decode("utf-8")
        elif jd_file.name.endswith(".pdf"):
            jd_text = extract_text_from_pdf(io.BytesIO(jd_file.read()))
        elif jd_file.name.endswith(".docx"):
            jd_text = extract_text_from_docx(io.BytesIO(jd_file.read()))
        else:
            st.error("Unsupported JD format.")
            st.stop()


        resume_folder = "tmp/resumes"
        os.makedirs(resume_folder, exist_ok=True)
        for resume in resumes:
            with open(os.path.join(resume_folder, resume.name), "wb") as f:
                f.write(resume.read())

        output_file = "tmp/parsed_resumes.csv"
        run_resume_parser(jd_text, resume_folder, output_file)

        df = pd.read_csv(output_file)
        st.session_state['parsed_df'] = df  # Store DataFrame in session state
        st.success("✅ Parsing Complete!")

# === Display Results ===
if 'parsed_df' in st.session_state:
    df = st.session_state['parsed_df']
    st.dataframe(df)

    st.download_button(
        label="📥 Download Results as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="parsed_resumes.csv",
        mime="text/csv"
    )

    # === Send Emails Section ===
    if "Email" in df.columns and "Status" in df.columns:
        st.subheader("📧 Send Emails to Candidates")

        if st.button("✉️ Send Emails Now"):
            sent = 0
            for _, row in df.iterrows():
                name = row.get("Name", "Candidate")
                email = row.get("Email", "")
                status = str(row.get("Status", "")).strip()

                if status in ["Shortlisted", "Rejected"] and email:
                    success = send_email(email, name, status)
                    if success:
                        sent += 1
            st.success(f"✅ Emails sent to {sent} candidates.")
    else:
        st.warning("❗️ 'Email' or 'Status' column not found in parsed data.")
