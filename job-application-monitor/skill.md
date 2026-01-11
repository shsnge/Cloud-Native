# Job Application Monitor

24/7 automated system that monitors email for job applications, scores candidates based on requirements, stores data in Google Sheets, and notifies high-scoring candidates via WhatsApp.

## Description

This workflow continuously monitors your email for incoming job applications and:
1. Reads and parses application emails
2. Extracts candidate information and CV attachments
3. Scores candidates 1-10 based on job requirements
4. Stores all data in Google Sheets
5. Sends WhatsApp notification for candidates scoring 8+
6. Sends auto-reply email to all applicants
7. Tracks all applications in real-time

## When to Use

Use this skill when you want to:
- Automate job application screening
- Filter candidates based on requirements
- Get instant notifications for top candidates
- Maintain a database of all applicants
- Send automated responses to applicants

## Features

- **24/7 Email Monitoring**: Continuously checks for new applications
- **CV Parsing**: Extracts data from PDF and DOCX resumes
- **Intelligent Scoring**: Scores candidates based on:
  - Skills match
  - Experience level
  - Education
  - Keywords in CV
- **Google Sheets Integration**: Real-time data storage
- **WhatsApp Notifications**: Instant alerts for 8+ scorers
- **Auto-Reply**: Sends confirmation emails to all candidates

## Setup

### Prerequisites

1. **Enable IMAP in Gmail**:
   - Go to Gmail Settings → Forwarding and POP/IMAP
   - Enable IMAP access
   - Save changes

2. **Google Sheets API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project
   - Enable Google Sheets API
   - Create a Service Account
   - Download credentials JSON
   - Create a new Google Sheet and share with service account email

3. **WhatsApp Setup** (for notifications):
   - Use Twilio API or Callmebot
   - Get your API credentials

4. **Install Required Python Packages**:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   pip install PyPDF2 python-docx
   pip install twilio
   ```

### Configuration

Create `config.json`:

```json
{
  "email": {
    "imap_server": "imap.gmail.com",
    "email_address": "your-email@gmail.com",
    "app_password": "your-app-password",
    "folder": "INBOX",
    "check_interval": 60
  },
  "google_sheets": {
    "credentials_file": "credentials.json",
    "spreadsheet_id": "your-sheet-id",
    "sheet_name": "Applications"
  },
  "whatsapp": {
    "service": "twilio",
    "account_sid": "your-twilio-sid",
    "auth_token": "your-twilio-token",
    "from_number": "whatsapp:+14155238886",
    "to_number": "whatsapp:+923001234567"
  },
  "scoring": {
    "passing_score": 8,
    "max_score": 10
  },
  "auto_reply": {
    "enabled": true,
    "subject": "Application Received - [Company Name]",
    "interview_days": 3
  }
}
```

### Job Requirements

Create `requirements.json` for each job position:

```json
{
  "position": "Senior Software Engineer",
  "required_skills": ["Python", "JavaScript", "React"],
  "preferred_skills": ["AWS", "Docker", "Kubernetes"],
  "min_experience": 3,
  "education": ["Bachelor's", "Master's"],
  "keywords": ["Full Stack", "API", "Database"]
}
```

## Usage

Start the monitor:

```bash
python monitor.py
```

The system will:
1. Connect to your email
2. Monitor for new messages (checking every 60 seconds)
3. Process new applications automatically
4. Update Google Sheets in real-time
5. Send WhatsApp notifications for top candidates
6. Send auto-reply emails

## Google Sheets Format

The sheet will have these columns:
- Timestamp
- Candidate Name
- Email
- Phone
- Position Applied
- Score (1-10)
- Skills Match
- Experience
- Education
- CV Link
- Status
- Notes

## Scoring Logic

| Criteria | Points |
|----------|--------|
| Required Skills Match | 0-3 |
| Preferred Skills | 0-2 |
| Experience Level | 0-2 |
| Education | 0-1 |
| Keywords Match | 0-2 |
| **Total** | **0-10** |

## Auto-Reply Email Template

```
Subject: Application Received - [Company Name]

Dear [Candidate Name],

Thank you for applying for the [Position] role at [Company Name].

We have received your application and it is currently under review. If your profile matches our requirements, you can expect to receive an interview call within 3 days.

Best regards,
HR Team
[Company Name]
```

## Files

- `monitor.py` - Main monitoring script
- `config.json` - Configuration file
- `requirements.json` - Job requirements
- `credentials.json` - Google Sheets API credentials
- `cv_parser.py` - CV parsing module
- `scorer.py` - Candidate scoring module
- `email_handler.py` - Email operations
- `sheets_handler.py` - Google Sheets operations
- `whatsapp_handler.py` - WhatsApp notifications
