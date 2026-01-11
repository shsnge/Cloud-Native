# Job Application Monitor - Setup Guide

## Quick Start

1. Install required Python packages:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   pip install PyPDF2 python-docx
   pip install twilio
   ```

2. Copy configuration templates:
   ```bash
   cp config.template.json config.json
   cp requirements.template.json requirements.json
   ```

3. Configure your credentials in `config.json` and `requirements.json`

4. Run the monitor:
   ```bash
   python monitor.py
   ```

---

## Configuration Steps

### 1. Gmail Setup (IMAP Access)

**Enable IMAP in Gmail:**
1. Go to Gmail Settings
2. Click "Forwarding and POP/IMAP"
3. Enable "IMAP access"
4. Save changes

**Generate App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate password for "Mail"
5. Copy to `config.json`:
   ```json
   "email": {
     "email_address": "your@gmail.com",
     "app_password": "xxxx xxxx xxxx xxxx"
   }
   ```

### 2. Google Sheets Setup

**Create Google Cloud Project:**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Search for "Google Sheets API" and enable it

**Create Service Account:**
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name it (e.g., "Job Application Monitor")
4. Click "Create and Continue"
5. Skip granting roles (optional)
6. Click "Done"

**Download Credentials:**
1. Click on the service account you created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" and click "Create"
5. Save as `credentials.json` in this folder

**Create Google Sheet:**
1. Go to https://sheets.google.com
2. Create a new spreadsheet
3. Copy the spreadsheet ID from URL (the long string between `/d/` and `/edit`)
4. Share the sheet with your service account email (from the JSON file):
   - Click "Share"
   - Paste service account email (looks like xxx@xxx.iam.gserviceaccount.com)
   - Give "Editor" access

**Update config.json:**
```json
"google_sheets": {
  "credentials_file": "credentials.json",
  "spreadsheet_id": "your-sheet-id-here",
  "sheet_name": "Applications"
}
```

### 3. WhatsApp Setup (Twilio)

**Create Twilio Account:**
1. Go to https://www.twilio.com/
2. Sign up for free account
3. Verify your email and phone number

**Get WhatsApp Credentials:**
1. Go to Twilio Console
2. Navigate to "Messaging" → "Try it out" → "Send a WhatsApp message"
3. Or go to "Console" → "Messaging" → "Settings" → "WhatsApp sandbox settings"

**Get Your Credentials:**
From Twilio Console Dashboard:
- Account SID
- Auth Token

**Update config.json:**
```json
"whatsapp": {
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "auth_token": "your_auth_token_here",
  "from_number": "whatsapp:+14155238886",
  "to_number": "whatsapp:+923001234567"
}
```

**Note:** For testing, use Twilio's WhatsApp sandbox first. For production, you'll need a dedicated WhatsApp number.

---

## Job Requirements Setup

Edit `requirements.json` based on your hiring needs:

```json
{
  "position": "Senior Software Engineer",
  "required_skills": ["Python", "JavaScript", "React"],
  "preferred_skills": ["AWS", "Docker"],
  "min_experience": 3,
  "education": ["Bachelor's", "Master's"],
  "keywords": ["Full Stack", "API", "Database"]
}
```

---

## Scoring System

| Criteria | Points | Description |
|----------|--------|-------------|
| Required Skills | 0-3 | Percentage of required skills found |
| Preferred Skills | 0-2 | Percentage of preferred skills found |
| Experience | 0-2 | Years of experience vs minimum required |
| Education | 0-1 | Match with required education |
| Keywords | 0-2 | Keywords found in CV |
| **Total** | **0-10** | **Final score** |

**Passing Score:** 8+ (configurable)

---

## How It Works

1. **Email Monitoring**: Checks Gmail every 60 seconds for new emails
2. **Application Detection**: Identifies job applications by subject keywords
3. **CV Extraction**: Downloads and parses PDF/DOCX attachments
4. **Scoring**: Scores candidate based on requirements.json
5. **Storage**: Adds candidate to Google Sheets
6. **WhatsApp Alert**: Notifies you if score is 8+
7. **Auto-Reply**: Sends confirmation email to applicant

---

## Google Sheet Format

| Timestamp | Name | Email | Phone | Position | Score | Feedback | Status | CV Path |
|-----------|------|-------|-------|----------|-------|----------|--------|---------|
| 2025-01-11 | John Doe | john@email.com | +1234567890 | Senior SE | 9 | Required Skills: 4/4 matched | Passed | cv_cache/... |

---

## Testing Without Full Setup

The monitor works in limited mode without full setup:
- ✅ Email monitoring works with Gmail only
- ⚠️ CV parsing requires `pip install PyPDF2 python-docx`
- ⚠️ Google Sheets requires service account setup
- ⚠️ WhatsApp requires Twilio setup
- ✅ Auto-reply works with Gmail only

---

## File Structure

```
job-application-monitor/
├── monitor.py              # Main monitoring script
├── config.template.json    # Configuration template
├── config.json            # Your actual config (create this)
├── requirements.template.json
├── requirements.json      # Job requirements (create this)
├── credentials.json       # Google Sheets credentials (create this)
├── processed_emails.txt   # Tracks processed emails (auto-created)
├── cv_cache/             # Downloaded CVs (auto-created)
├── monitor.log           # Activity log (auto-created)
└── SETUP.md             # This file
```

---

## Running the Monitor

**Start:**
```bash
python monitor.py
```

**Stop:** Press `Ctrl+C`

**Run in background (Linux/Mac):**
```bash
nohup python monitor.py &
```

**Run in background (Windows):**
```bash
start /B python monitor.py
```

---

## Troubleshooting

**IMAP Error: Authentication failed**
- Verify app password is correct
- Ensure 2-Step Verification is enabled
- Check IMAP is enabled in Gmail settings

**Google Sheets Error: Invalid credentials**
- Verify credentials.json path is correct
- Check service account email has sheet access
- Ensure spreadsheet ID is correct

**WhatsApp Error: Unauthorized**
- Verify Twilio credentials
- Check phone number format (must include country code)
- For sandbox, join sandbox first

**CV Parsing Error: Cannot extract text**
- Install CV parsing libraries: `pip install PyPDF2 python-docx`
- Some PDFs may be scanned images (not text)

---

## Security Notes

- **Never commit** credentials.json, config.json to version control
- **Add to .gitignore:**
  ```
   credentials.json
   config.json
   processed_emails.txt
   cv_cache/
   monitor.log
  ```
- **App Passwords** can be revoked at any time from Google Account settings
- **Service Account** can be disabled if compromised
