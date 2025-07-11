from app.emailer import process_csv_and_send_emails

if __name__ == "__main__":
    process_csv_and_send_emails("outputs/parsed_resumes.csv")
