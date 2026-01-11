# Job Post Workflow - Setup Guide

## Quick Start

1. Copy the configuration template:
   ```bash
   cp config.template.json config.json
   ```

2. Edit `config.json` with your credentials

3. Run the workflow:
   ```bash
   python workflow.py
   ```

## Gmail Setup (for Email Notifications)

### Option 1: Gmail SMTP (Recommended - Easiest)

1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification (if not already enabled)
   - Go to "App passwords" under 2-Step Verification
   - Select "Mail" and your computer
   - Copy the generated 16-character password

3. Add to config.json:
   ```json
   "email": {
     "method": "gmail_smtp",
     "sender_email": "your-email@gmail.com",
     "app_password": "abcd efgh ijkl mnop",
     "recipient_email": "your-email@gmail.com"
   }
   ```

### Option 2: Gmail API (Advanced)

Requires additional setup with Google Cloud Console and OAuth credentials.

## LinkedIn Setup

1. Go to https://www.linkedin.com/developers/
2. Create a new application
3. Get your Access Token (use OAuth 2.0 tools like Postman)
4. Find your Person URN from your LinkedIn profile URL

### Getting Access Token via Postman:
1. Create OAuth 2.0 request in Postman
2. Auth URL: `https://www.linkedin.com/oauth/v2/authorization`
3. Access Token URL: `https://www.linkedin.com/oauth/v2/accessToken`
4. Client ID & Secret from your LinkedIn app
5. Scope: `w_member_social`

### Finding your Person URN:
- Go to your LinkedIn profile
- The ID is in the URL: `linkedin.com/in/username/`
- Or use: `urn:li:person:PROFILE_ID`

## Facebook Setup

1. Go to https://developers.facebook.com/
2. Create a new app
3. Add "Page Public Access" product
4. Generate a Page Access Token with `pages_manage_posts` permission

### Finding your Page ID:
- Go to your Facebook Page
- Click "About" on the left sidebar
- Your Page ID is listed under "Page Info"

## Required Python Packages

```bash
pip install requests
```

For Gmail API (if using API method):
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Testing Without Credentials

The workflow works in "console mode" for testing without full setup:
- Email will be printed to console
- Social posting will show configuration errors (but won't crash)

## Troubleshooting

**Gmail SMTP: Authentication Failed**
- Make sure 2-Factor Authentication is enabled
- Generate a new App Password
- Check for typos in the 16-character password

**LinkedIn: 403 Forbidden**
- Verify your access token is valid (tokens expire)
- Check that your app has correct permissions
- Ensure person_URN format is correct

**Facebook: Invalid Token**
- Generate a new Page Access Token
- Verify `pages_manage_posts` permission is granted
- Check token hasn't expired

## File Structure

```
job-post-workflow/
├── skill.md              # Skill definition
├── workflow.py           # Main workflow script
├── config.template.json  # Configuration template
├── config.json          # Your actual config (create this)
├── SETUP.md             # This file
└── job_post_*.txt       # Generated job posts
```
