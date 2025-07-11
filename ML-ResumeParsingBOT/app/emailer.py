# app/emailer.py (Revised)
import smtplib
import os
import pandas as pd # Import pandas here
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
SENDER_EMAIL = os.getenv("EMAIL")
SENDER_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(to_email, name, status):
    # ... (Your existing send_email function code) ...
    if status == "Shortlisted":
        subject = "You’ve Been Shortlisted"
        body = f"Dear {name},\n\nYou are shortlisted for the role.\n\n- Accenture"
    elif status == "Rejected":
        subject = "Application Update"
        body = f"Dear {name},\n\nWe won’t be proceeding further.\n\n- Accenture"
    else:
        return False

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
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


def process_csv_and_send_emails(csv_file_path):
    """
    Reads a CSV file containing parsed resume data and sends emails
    to candidates based on their status.
    """
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    sent_count = 0
    if "Email" in df.columns and "Name" in df.columns and "Status" in df.columns:
        for index, row in df.iterrows():
            name = row.get("Name", "Candidate")
            email = row.get("Email", "")
            status = str(row.get("Status", "")).strip()

            if status in ["Shortlisted", "Rejected"] and email:
                if send_email(email, name, status):
                    sent_count += 1
                else:
                    print(f"Skipped email for {name} ({email}) due to an error or invalid status.")
            else:
                print(f"Skipped email for row {index}: Missing email, name, or status is not 'Shortlisted' or 'Rejected'.")
        print(f"\nCompleted: Sent emails to {sent_count} candidates.")
    else:
        print("Error: 'Email', 'Name', or 'Status' columns not found in the CSV.")

