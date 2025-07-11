from app.parser import run_resume_parser, extract_text_from_pdf, extract_text_from_docx
import os

def load_jd_text(jd_path):
    ext = jd_path.lower().split('.')[-1]
    if ext == "pdf":
        return extract_text_from_pdf(jd_path)
    elif ext == "docx":
        return extract_text_from_docx(jd_path)
    elif ext == "txt":
        with open(jd_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported JD format. Please use TXT, PDF, or DOCX.")

if __name__ == "__main__":
    jd_path = "JD.txt"  # Replace with "JD.pdf" or "JD.docx" as needed
    resume_folder = "resumes"
    output_file = "outputs/parsed_resumes.csv"

    jd_text = load_jd_text(jd_path)

    run_resume_parser(jd_path=None, jd_text=jd_text, resume_folder=resume_folder, output_file=output_file)
