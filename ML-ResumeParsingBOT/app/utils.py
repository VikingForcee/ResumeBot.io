import re
import pdfplumber
import docx

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    patterns = [r'(\+91[\-\s]?)?[789]\d{9}', r'\d{3}[\-\.\s]?\d{3}[\-\.\s]?\d{4}']
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""

def extract_name(text):
    for line in text.strip().split('\n')[:5]:
        if line and not re.search(r'@|resume|cv', line.lower()):
            if len(line.split()) <= 5:
                return line.strip()
    return ""
