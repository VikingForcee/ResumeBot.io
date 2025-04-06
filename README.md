# ResumeBot.io
---
## 🚀 Project Overview

**ResumeBot.io** is an end-to-end **pipeline** and intelligent **agent** that automates your hiring workflow:
1. **Fetch** resumes from your Gmail inbox based on a subject filter.
2. **Extract** key details (name, email, phone, education, skills, experience, projects, achievements).
3. **Match** each resume against your Job Description (JD) and score candidates.
4. **Shortlist** top candidates and generate a CSV report.
5. **Send** personalized emails to shortlisted or rejected applicants.

All you do is upload your JD and let the agent handle the rest.

---

## 🎨 Architecture Diagram

```text
        +----------------+        +------------------+        +------------------+
        |                |        |                  |        |                  |
        |   Email Agent  |------->|  Resume Pipeline |------->|  Shortlist Agent |
        |(IMAP Fetcher)  |        | (Parser & Scorer)|        | (Email Sender)   |
        |                |        |                  |        |                  |
        +----------------+        +------------------+        +------------------+
                    \                         |                          /
                     \                        |                         /
                      \                       v                        /
                       \             +------------------+             /
                        \------------|   CSV Reporter   |------------/
                                     | (Downloadable)   |
                                     +------------------+
```

---

## 📦 Features

- **Email Integration**: Automatically downloads PDF/DOCX resumes from Gmail.
- **JD Uploader**: Upload your job description file (TXT/PDF/DOCX).
- **Resume Parser**: Extracts contact info, education, skills, experience, projects, and achievements.
- **Scoring Engine**: Assigns weights and TF-IDF JD match points to rank candidates.
- **Shortlist Agent**: Flags resumes as `Shortlisted`, `To be Reviewed`, or `Rejected`.
- **Report Generator**: Exports results to `parsed_resumes_final.csv`.
- **Email Notifier**: Sends personalized acceptance or rejection emails.

---

## 📂 Project Structure

```
resumebot.io/
├── app.py               # Flask application
├── requirements.txt     # Python dependencies
├── Procfile             # For Heroku deployment
├── templates/           # HTML templates
│   ├── index.html       # JD upload page
│   ├── upload_resumes.html
│   ├── results.html     # Display parsed results
│   └── email_download.html
├── static/              # CSS/JS assets
└── README.md            # This file
```

---
---

## 🤝 Contributing

1. Fork the repo.
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add YourFeature"
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request.

---
