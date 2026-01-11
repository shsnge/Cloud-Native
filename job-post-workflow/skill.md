# Job Post Workflow

Automated workflow for creating professional job postings, notifying you via email for review, and posting to LinkedIn and Facebook.

## Description

This skill streamlines the hiring process by:
1. Gathering job details through interactive prompts
2. Generating a professional job posting
3. Sending you an email with the job post for review
4. Allowing you to post directly to LinkedIn and/or Facebook after approval

## When to Use

Use this skill when you need to:
- Create and publish job listings quickly
- Maintain consistent job post formatting
- Review job posts before publishing
- Post jobs to multiple platforms simultaneously
- Streamline your hiring workflow

## Setup

### Prerequisites

1. **Gmail API Setup** (for email notifications):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials.json and place it in this skill's folder
   - Or use an App Password with Gmail SMTP

2. **LinkedIn Setup** (for posting):
   - Create a LinkedIn Developer account
   - Create an application to get Client ID and Client Secret
   - Set up OAuth 2.0 authentication

3. **Facebook Setup** (for posting):
   - Create a Facebook Developer account
   - Create a Facebook App
   - Get Page Access Token for your company page

### Configuration

Create a `config.json` file in this skill's directory:

```json
{
  "email": {
    "method": "gmail_smtp",
    "sender_email": "your-email@gmail.com",
    "app_password": "your-app-password",
    "recipient_email": "your-email@gmail.com"
  },
  "linkedin": {
    "access_token": "your-linkedin-access-token",
    "person_urn": "urn:li:person:your-person-id"
  },
  "facebook": {
    "page_id": "your-page-id",
    "page_access_token": "your-page-access-token"
  }
}
```

## Usage

Simply invoke the skill and answer the prompts:

```
Create a job post for a Senior Software Engineer position
```

The workflow will:
1. Ask for job details (title, description, requirements, benefits, etc.)
2. Generate a formatted job post
3. Email you the post for review
4. Ask which platforms to post to
5. Publish to your selected platforms

## Example Output

The generated job post includes:
- Eye-catching title
- Company description
- Role overview
- Responsibilities
- Requirements
- Benefits/perks
- Clear call-to-action

## Files

- `workflow.py` - Main workflow implementation
- `config.json` - Your API credentials (create this)
- `job_template.md` - Job post template (optional, can customize)
