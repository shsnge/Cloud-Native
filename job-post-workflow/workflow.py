#!/usr/bin/env python3
"""
Job Post Workflow - Automated job posting creation and distribution
Creates job posts, sends email notifications, and posts to LinkedIn/Facebook
"""

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional

# Try to import requests, provide helpful message if missing
try:
    import requests
except ImportError:
    print("Note: 'requests' library not installed. Social posting will be limited.")
    requests = None


class JobPostWorkflow:
    """Main workflow class for creating and distributing job posts"""

    def __init__(self, config_path: str = None):
        """Initialize the workflow with configuration"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')

        self.config_path = config_path
        self.config = self._load_config()
        self.job_data = {}

    def _load_config(self) -> Dict:
        """Load configuration from file or return defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid config.json in {self.config_path}")
                return self._default_config()
        else:
            print(f"Config file not found at {self.config_path}")
            print("Using default configuration. Please create config.json for full functionality.")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "email": {
                "method": "console",
                "sender_email": "",
                "recipient_email": ""
            },
            "linkedin": {
                "access_token": "",
                "person_urn": ""
            },
            "facebook": {
                "page_id": "",
                "page_access_token": ""
            }
        }

    def gather_job_details(self) -> Dict:
        """Interactive prompt to gather job details"""
        print("\n" + "="*60)
        print("JOB POST CREATION WORKFLOW")
        print("="*60 + "\n")

        job_data = {
            "job_title": input("Job Title (e.g., Senior Software Engineer): ").strip(),
            "company_name": input("Company Name: ").strip(),
            "location": input("Location (e.g., Remote / New York, NY): ").strip(),
            "employment_type": input("Employment Type (Full-time/Part-time/Contract): ").strip() or "Full-time",
            "salary_range": input("Salary Range (e.g., $80,000 - $120,000 or 'Competitive'): ").strip() or "Competitive",
        }

        print("\n--- Job Description (brief overview) ---")
        job_data["description"] = input("Enter a brief description of the role: ").strip()

        print("\n--- Responsibilities (enter one per line, press Enter twice when done) ---")
        job_data["responsibilities"] = self._get_multiline_input()

        print("\n--- Requirements (enter one per line, press Enter twice when done) ---")
        job_data["requirements"] = self._get_multiline_input()

        print("\n--- Benefits/Perks (enter one per line, press Enter twice when done) ---")
        job_data["benefits"] = self._get_multiline_input() or ["Competitive salary", "Flexible work schedule"]

        job_data["application_url"] = input("\nApplication URL or Email (where to apply): ").strip()

        job_data["created_date"] = datetime.now().strftime("%Y-%m-%d")

        self.job_data = job_data
        return job_data

    def _get_multiline_input(self) -> list:
        """Helper to get multiple lines of input"""
        lines = []
        while True:
            line = input("  > ").strip()
            if not line:
                break
            lines.append(line)
        return lines

    def generate_job_post(self, job_data: Dict = None) -> str:
        """Generate a formatted job post"""
        if job_data is None:
            job_data = self.job_data

        if not job_data:
            raise ValueError("No job data available. Run gather_job_details() first.")

        # Build the job post
        post_lines = [
            f"🚀 {job_data['job_title']} at {job_data['company_name']}",
            "",
            f"📍 Location: {job_data['location']}",
            f"💼 Type: {job_data['employment_type']}",
            f"💰 Salary: {job_data['salary_range']}",
            "",
            "─" * 50,
            "",
            "About the Role:",
            job_data.get('description', 'Join our team!'),
            "",
            "Key Responsibilities:",
        ]

        for resp in job_data.get('responsibilities', []):
            post_lines.append(f"  • {resp}")

        post_lines.extend([
            "",
            "Requirements:",
        ])

        for req in job_data.get('requirements', []):
            post_lines.append(f"  • {req}")

        post_lines.extend([
            "",
            "What We Offer:",
        ])

        for benefit in job_data.get('benefits', []):
            post_lines.append(f"  ✓ {benefit}")

        post_lines.extend([
            "",
            "─" * 50,
            "",
            f"📧 Apply: {job_data.get('application_url', 'Contact us for details')}",
            "",
            f"#hiring #{job_data['company_name'].replace(' ', '')} #job",
        ])

        return "\n".join(post_lines)

    def send_email_notification(self, job_post: str, job_data: Dict = None) -> bool:
        """Send email with the job post for review"""
        if job_data is None:
            job_data = self.job_data

        email_config = self.config.get('email', {})
        method = email_config.get('method', 'console')

        subject = f"Job Post Ready for Review: {job_data.get('job_title', 'Position')}"

        if method == 'gmail_smtp':
            return self._send_via_gmail_smtp(subject, job_post, email_config)
        elif method == 'gmail_api':
            return self._send_via_gmail_api(subject, job_post, email_config)
        else:
            # Console fallback
            print("\n" + "="*60)
            print("EMAIL PREVIEW (Console Mode)")
            print("="*60)
            print(f"To: {email_config.get('recipient_email', 'you@example.com')}")
            print(f"Subject: {subject}")
            print("\n" + job_post)
            print("="*60 + "\n")
            return True

    def _send_via_gmail_smtp(self, subject: str, body: str, config: Dict) -> bool:
        """Send email using Gmail SMTP"""
        try:
            sender_email = config.get('sender_email')
            app_password = config.get('app_password')
            recipient_email = config.get('recipient_email', sender_email)

            if not all([sender_email, app_password]):
                print("Gmail SMTP credentials not configured. Showing preview instead:")
                print(f"\nTo: {recipient_email}")
                print(f"Subject: {subject}")
                print(f"\n{body}")
                return False

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send via SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)

            print(f"✓ Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False

    def _send_via_gmail_api(self, subject: str, body: str, config: Dict) -> bool:
        """Send email using Gmail API (requires google-api-python-client)"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            from email.mime.text import MIMEText
            import base64

            # This would require proper token.json setup
            print("Gmail API method requires additional OAuth setup.")
            print("Consider using Gmail SMTP method instead (simpler).")
            return False

        except ImportError:
            print("google-api-python-client not installed.")
            print("Install with: pip install google-api-python-client")
            return False

    def post_to_linkedin(self, job_post: str) -> bool:
        """Post job to LinkedIn"""
        if requests is None:
            print("✗ 'requests' library required for LinkedIn posting")
            return False

        linkedin_config = self.config.get('linkedin', {})
        access_token = linkedin_config.get('access_token')

        if not access_token:
            print("✗ LinkedIn access token not configured")
            print("Add your access token to config.json")
            return False

        try:
            # LinkedIn UGC Post API
            url = "https://api.linkedin.com/v2/ugcPosts"

            person_urn = linkedin_config.get('person_urn', '')
            if not person_urn:
                print("✗ LinkedIn person URN not configured")
                return False

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": job_post
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                print("✓ Successfully posted to LinkedIn!")
                return True
            else:
                print(f"✗ LinkedIn posting failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error posting to LinkedIn: {e}")
            return False

    def post_to_facebook(self, job_post: str) -> bool:
        """Post job to Facebook Page"""
        if requests is None:
            print("✗ 'requests' library required for Facebook posting")
            return False

        fb_config = self.config.get('facebook', {})
        page_id = fb_config.get('page_id')
        page_access_token = fb_config.get('page_access_token')

        if not all([page_id, page_access_token]):
            print("✗ Facebook credentials not configured")
            print("Add page_id and page_access_token to config.json")
            return False

        try:
            url = f"https://graph.facebook.com/{page_id}/feed"
            params = {
                "message": job_post,
                "access_token": page_access_token
            }

            response = requests.post(url, params=params)

            if response.status_code in [200, 201]:
                print("✓ Successfully posted to Facebook!")
                return True
            else:
                print(f"✗ Facebook posting failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error posting to Facebook: {e}")
            return False

    def run(self):
        """Run the complete workflow"""
        # Step 1: Gather job details
        print("\n📋 Step 1: Gathering job details...")
        self.gather_job_details()

        # Step 2: Generate job post
        print("\n✍️  Step 2: Generating job post...")
        job_post = self.generate_job_post()

        # Step 3: Send email notification
        print("\n📧 Step 3: Sending email notification...")
        self.send_email_notification(job_post)

        # Step 4: Ask which platforms to post to
        print("\n📱 Step 4: Choose platforms to post to:")
        print("  1. LinkedIn only")
        print("  2. Facebook only")
        print("  3. Both platforms")
        print("  4. Skip posting (email sent for review)")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            self.post_to_linkedin(job_post)
        elif choice == '2':
            self.post_to_facebook(job_post)
        elif choice == '3':
            linkedin_ok = self.post_to_linkedin(job_post)
            facebook_ok = self.post_to_facebook(job_post)
            if linkedin_ok and facebook_ok:
                print("\n✓ Job post successfully published to both platforms!")
        elif choice == '4':
            print("\n✓ Email sent! Review and post manually when ready.")
        else:
            print("\nInvalid choice. Email has been sent for your review.")

        # Save job post to file
        self._save_job_post(job_post)

        print("\n" + "="*60)
        print("WORKFLOW COMPLETE")
        print("="*60 + "\n")

    def _save_job_post(self, job_post: str):
        """Save job post to a file"""
        filename = f"job_post_{self.job_data.get('job_title', 'position').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(os.path.dirname(__file__), filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(job_post)
            print(f"📄 Job post saved to: {filename}")
        except Exception as e:
            print(f"Note: Could not save job post file: {e}")


def main():
    """Main entry point"""
    workflow = JobPostWorkflow()
    workflow.run()


if __name__ == "__main__":
    main()
