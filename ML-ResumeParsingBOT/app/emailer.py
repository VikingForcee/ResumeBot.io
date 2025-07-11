import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()
SENDER_EMAIL = os.getenv("EMAIL")
SENDER_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(to_email, name, status):
    if status == "Shortlisted":
        subject = "You’ve Been Shortlisted"
        body = f"Dear {name},\n\nYou are shortlisted for the role.\n\n- Accenture"
    elif status == "Rejected":
        subject = "Application Update"
        body = f"Dear {name},\n\nWe won’t be proceeding further.\n\n- Accenture"
    else:
        return
    print(f"Trying to send email to {to_email} with status {status}")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        print("Sending email now...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed: {to_email} — {e}")
        return False

def process_csv_and_send_emails(csv_path):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        if pd.notna(row['Email']) and row['Status'] in ["Shortlisted", "Rejected"]:
            send_email(row['Email'], row.get('Name', 'Candidate'), row['Status'])
