#!/usr/bin/env python3
"""
Job Application Monitor - 24/7 Email Monitoring & Candidate Scoring System
Monitors email for job applications, scores candidates, stores in Google Sheets,
and sends WhatsApp notifications for high-scoring candidates.
"""

import imaplib
import email
import json
import os
import time
import re
from datetime import datetime
from email.header import decode_header
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    logger.warning("Google Sheets libraries not installed. Run: pip install google-api-python-client")

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. Run: pip install twilio")

try:
    import PyPDF2
    import docx
    CV_PARSING_AVAILABLE = True
except ImportError:
    CV_PARSING_AVAILABLE = False
    logger.warning("CV parsing libraries not installed. Run: pip install PyPDF2 python-docx")


class JobApplicationMonitor:
    """Main monitor class for job application processing"""

    def __init__(self, config_path='config.json', requirements_path='requirements.json'):
        """Initialize the monitor with configuration"""
        self.config = self._load_config(config_path)
        self.requirements = self._load_requirements(requirements_path)
        self.processed_emails = set()
        self.sent_reply_emails = set()  # Track emails we've already replied to
        self.load_processed_emails()
        self.load_sent_replies()

        # Initialize handlers
        self.sheets_handler = None
        self.whatsapp_handler = None
        self.email_handler = None

        # Initialize Google Sheets (if enabled)
        gs_config = self.config.get('google_sheets', {})
        if GOOGLE_SHEETS_AVAILABLE and gs_config.get('enabled', False):
            self.sheets_handler = GoogleSheetsHandler(gs_config)
        else:
            self.sheets_handler = None
            logger.info("Google Sheets disabled. Using CSV storage.")

        # Initialize CSV storage (if enabled)
        csv_config = self.config.get('csv_storage', {})
        if csv_config.get('enabled', True):
            from csv_storage import CSVStorage
            self.csv_handler = CSVStorage(csv_config.get('file', 'applications_backup.csv'))
            logger.info("CSV storage enabled.")
        else:
            self.csv_handler = None

        if TWILIO_AVAILABLE:
            self.whatsapp_handler = WhatsAppHandler(self.config.get('whatsapp', {}))

        self.email_handler = EmailHandler(self.config.get('email', {}))

    def _load_config(self, path):
        """Load configuration from file"""
        default_config = {
            "email": {
                "imap_server": "imap.gmail.com",
                "email_address": "",
                "app_password": "",
                "folder": "INBOX",
                "check_interval": 60
            },
            "google_sheets": {
                "credentials_file": "credentials.json",
                "spreadsheet_id": "",
                "sheet_name": "Applications"
            },
            "whatsapp": {
                "service": "twilio",
                "account_sid": "",
                "auth_token": "",
                "from_number": "",
                "to_number": ""
            },
            "scoring": {
                "passing_score": 8,
                "max_score": 10
            },
            "auto_reply": {
                "enabled": True,
                "subject": "Application Received",
                "interview_days": 3,
                "company_name": "Our Company"
            }
        }

        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except json.JSONDecodeError:
                logger.error(f"Invalid config.json in {path}")

        return default_config

    def _load_requirements(self, path):
        """Load job requirements from file"""
        default_requirements = {
            "position": "General",
            "required_skills": [],
            "preferred_skills": [],
            "min_experience": 0,
            "education": [],
            "keywords": []
        }

        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid requirements.json in {path}")

        return default_requirements

    def load_processed_emails(self):
        """Load list of already processed emails"""
        if os.path.exists('processed_emails.txt'):
            with open('processed_emails.txt', 'r') as f:
                self.processed_emails = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.processed_emails)} previously processed emails")

    def save_processed_email(self, email_id):
        """Save processed email ID to avoid reprocessing"""
        self.processed_emails.add(email_id)
        with open('processed_emails.txt', 'a') as f:
            f.write(f"{email_id}\n")

    def load_sent_replies(self):
        """Load list of emails we've already replied to"""
        if os.path.exists('sent_replies.txt'):
            with open('sent_replies.txt', 'r') as f:
                self.sent_reply_emails = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.sent_reply_emails)} previously sent replies")

    def save_sent_reply(self, identifier):
        """Save sent reply identifier to avoid duplicate emails"""
        self.sent_reply_emails.add(identifier)
        with open('sent_replies.txt', 'a') as f:
            f.write(f"{identifier}\n")

    def connect_email(self):
        """Connect to email server via IMAP"""
        try:
            email_config = self.config.get('email', {})
            imap_server = email_config.get('imap_server', 'imap.gmail.com')
            email_address = email_config.get('email_address')
            app_password = email_config.get('app_password')

            if not email_address or not app_password:
                logger.error("Email credentials not configured")
                return None

            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_address, app_password)
            mail.select(email_config.get('folder', 'INBOX'))

            logger.info(f"Connected to email: {email_address}")
            return mail

        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return None

    def process_new_emails(self, mail):
        """Process all emails from last 7 days (read or unread)"""
        try:
            from datetime import timedelta

            # Calculate date 7 days ago
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y')

            # Search ALL emails from last 7 days (not just UNSEEN)
            search_criteria = f'SINCE {seven_days_ago}'
            logger.info(f"Searching for emails with criteria: {search_criteria}")

            status, messages = mail.search(None, search_criteria)

            if status != 'OK':
                return

            email_ids = messages[0].split()

            if not email_ids:
                logger.debug("No emails found in last 7 days")
                return

            logger.info(f"Found {len(email_ids)} emails from last 7 days")

            # Limit to most recent 100 emails to avoid overload
            email_ids = email_ids[-100:] if len(email_ids) > 100 else email_ids
            logger.info(f"Processing {len(email_ids)} most recent emails")

            for email_id in email_ids:
                email_id_str = email_id.decode()

                # Skip if already processed
                if email_id_str in self.processed_emails:
                    continue

                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                if status == 'OK':
                    self.process_application(msg_data[0], email_id_str)
                    self.save_processed_email(email_id_str)

        except Exception as e:
            logger.error(f"Error processing emails: {e}")

    def process_application(self, msg_data, email_id):
        """Process a single job application email"""
        try:
            # Parse email
            msg = email.message_from_bytes(msg_data[1])

            # Extract email details
            from_header = msg.get('From', '')
            subject = msg.get('Subject', '')
            sender_email = self.extract_email(from_header)
            sender_name = self.extract_name(from_header)

            logger.info(f"Processing email from: {sender_name} ({sender_email})")
            logger.info(f"Subject: {subject}")

            # Validate sender email - skip auto-reply if invalid
            if not sender_email or not self._is_valid_email(sender_email):
                logger.error(f"Invalid sender email: '{sender_email}'. Skipping auto-reply to avoid errors.")
                sender_email = ''  # Set to empty to prevent sending

            # Skip automated/no-reply addresses
            if sender_email and self._is_automated_email(sender_email):
                logger.warning(f"Automated email address detected: {sender_email}. Skipping auto-reply.")
                sender_email = ''  # Set to empty to prevent sending

            # Check if this is a job application (basic keyword check)
            if not self.is_job_application(subject, msg):
                logger.info("Not a job application, skipping")
                return

            # Extract candidate data
            candidate_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': sender_name,
                'email': sender_email,
                'subject': subject,
                'position': self.extract_position(subject),
                'phone': self.extract_phone(msg),
                'cv_content': '',
                'cv_path': ''
            }

            # Process attachments (CV)
            cv_content = self.extract_cv_from_email(msg)
            if cv_content:
                candidate_data['cv_content'] = cv_content['text']
                candidate_data['cv_path'] = cv_content.get('path', '')

            # Score the candidate
            score_data = self.score_candidate(candidate_data)
            candidate_data.update(score_data)

            # Store in Google Sheets or CSV
            if self.sheets_handler:
                self.sheets_handler.add_candidate(candidate_data)
            elif self.csv_handler:
                self.csv_handler.add_candidate(candidate_data)
            else:
                logger.warning("No storage handler available. Candidate data not saved.")

            # Send WhatsApp notification if score is 8+
            passing_score = self.config.get('scoring', {}).get('passing_score', 8)
            if candidate_data['score'] >= passing_score:
                self.send_whatsapp_notification(candidate_data)

            # Send auto-reply email (only once per unique application)
            if self.config.get('auto_reply', {}).get('enabled', True) and sender_email:
                # Create unique identifier for this application
                # Use sender email + date to prevent duplicate replies on same day
                app_identifier = f"{sender_email}_{datetime.now().strftime('%Y-%m-%d')}"

                # Check if we've already replied to this sender today
                if app_identifier not in self.sent_reply_emails:
                    success = self.send_auto_reply(candidate_data)
                    if success:
                        self.save_sent_reply(app_identifier)
                        logger.info(f"Auto-reply sent to {sender_email}")
                    else:
                        logger.error(f"Failed to send auto-reply to {sender_email}")
                else:
                    logger.info(f"Already replied to {sender_email} today. Skipping duplicate email.")

            logger.info(f"Application processed. Score: {candidate_data['score']}/10")

        except Exception as e:
            logger.error(f"Error processing application: {e}")

    def is_job_application(self, subject, msg):
        """Check if email is a job application"""
        application_keywords = ['apply', 'application', 'resume', 'cv', 'job', 'position',
                                'hiring', 'vacancy', 'career', 'opportunity', 'role']

        subject_lower = subject.lower()
        for keyword in application_keywords:
            if keyword in subject_lower:
                logger.info(f"Job application detected by keyword '{keyword}' in subject")
                return True

        # Check for CV/Resume attachments
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                filename_lower = filename.lower()
                if any(ext in filename_lower for ext in ['.pdf', '.doc', '.docx']):
                    if any(keyword in filename_lower for keyword in ['cv', 'resume', 'curriculum', 'vitae']):
                        logger.info(f"Job application detected by CV attachment: {filename}")
                        return True

        # Check sender domain - if from job portals
        from_header = msg.get('From', '').lower()
        job_portal_domains = ['linkedin.com', 'indeed.com', 'glassdoor.com', 'rozee.pk',
                             'bayt.com', 'naukrigulf.com', 'monster.com']
        for domain in job_portal_domains:
            if domain in from_header:
                logger.info(f"Job application detected from job portal: {domain}")
                return True

        logger.info(f"Not a job application. Subject: {subject[:50]}...")
        return False

    def extract_position(self, subject):
        """Extract job position from subject line"""
        # Clean the subject - decode if needed
        clean_subject = subject.strip()

        # Try to decode if encoded
        if isinstance(clean_subject, bytes):
            clean_subject = clean_subject.decode('utf-8', errors='ignore')

        logger.info(f"Extracting position from subject: {clean_subject}")

        # Common patterns - ordered by priority
        patterns = [
            # "applying for Frontend Developer"
            r'applying\s+for\s+(?:the\s+)?(.+?)(?:\s+(?:position|role|at|@)|$)',
            # "Frontend Developer application"
            r'^(.+?)\s+(?:application|apply|job|position)',
            # "for Frontend Developer position"
            r'for\s+(?:the\s+)?(.+?)(?:\s+position|:\s*$|[-–—]|$)',
            # "position: Frontend Developer"
            r'position:\s*(.+?)(?:\s+[-–—]|$)',
            # "role: Frontend Developer"
            r'role:\s*(.+?)(?:\s+[-–—]|$)',
            # "application for Frontend Developer"
            r'application\s+(?:for|to)\s+(?:the\s+)?(.+?)(?:\s+[-–—]|at|@|job)',
            # "@Frontend Developer" or "- Frontend Developer"
            r'[@\-]\s*(.+?)(?:\s+job|:\s*$|[-–—])',
        ]

        for pattern in patterns:
            match = re.search(pattern, clean_subject, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                # Clean up the position title
                position = re.sub(r'[-–_]', ' ', position)  # Replace dashes with space
                # Remove common suffixes
                position = re.sub(r'\s+(position|role|job|application|at|@|in).*', '', position, flags=re.IGNORECASE).strip()
                position = ' '.join(word.capitalize() for word in position.split())  # Title case

                if position and len(position) > 2:
                    logger.info(f"Position extracted via pattern: {position}")
                    return position

        # If no pattern matches, try to find common job titles in subject
        common_titles = [
            'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
            'Software Engineer', 'Senior Software Engineer', 'Junior Software Engineer',
            'Web Developer', 'Mobile Developer', 'DevOps Engineer',
            'Data Scientist', 'Machine Learning Engineer', 'AI Engineer',
            'Product Manager', 'Project Manager', 'UI/UX Designer',
            'QA Engineer', 'Software Tester', 'Business Analyst',
            'React Developer', 'Angular Developer', 'Vue Developer',
            'Node.js Developer', 'Python Developer', 'Java Developer'
        ]

        subject_lower = clean_subject.lower()
        for title in common_titles:
            if title.lower() in subject_lower:
                logger.info(f"Position matched from common titles: {title}")
                return title

        # Last resort: extract first few meaningful words
        words = clean_subject.split()
        if len(words) >= 2:
            # Try taking first 2-3 words as position
            potential_position = ' '.join(words[:3])
            # Clean it up
            potential_position = re.sub(r'\s+(application|apply|for|job|position|role|at|@).*', '', potential_position, flags=re.IGNORECASE).strip()
            potential_position = ' '.join(word.capitalize() for word in potential_position.split())

            if potential_position and len(potential_position) > 5:
                logger.info(f"Position extracted from first words: {potential_position}")
                return potential_position

        # Return default from requirements if no match
        default_pos = self.requirements.get('position', 'Software Engineer')
        logger.warning(f"Could not extract position, using default: {default_pos}")
        return default_pos

    def extract_email(self, from_header):
        """Extract and validate email address from From header"""
        # Try to extract email from <email> format
        match = re.search(r'<(.+?)>', from_header)
        if match:
            email = match.group(1).strip()
            # Basic email validation
            if self._is_valid_email(email):
                return email

        # Try to extract email without brackets
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
        if match:
            email = match.group(0).strip()
            if self._is_valid_email(email):
                return email

        # Return the original header if no valid email found
        logger.warning(f"Could not extract valid email from: {from_header}")
        return ''

    def _is_valid_email(self, email):
        """Basic email validation"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _is_automated_email(self, email):
        """Check if email is an automated/no-reply address"""
        if not email:
            return False

        automated_patterns = [
            'noreply', 'no-reply', 'no_reply',
            'donotreply', 'do-not-reply', 'do_not_reply',
            'auto', 'automated', 'bot', 'robot',
            'notification', 'notify', 'alert',
            'mailer', 'daemon', 'server',
            'academic', 'premium', 'service'
        ]

        email_lower = email.lower()

        # Check for automated patterns in email
        for pattern in automated_patterns:
            if pattern in email_lower:
                return True

        # Check for common automated domains
        automated_domains = [
            '@linkedin.com',
            '@indeed.com',
            '@glassdoor.com',
            '@mailchimp.com',
            '@sendgrid.com',
            '@amazonses.com'
        ]

        for domain in automated_domains:
            if domain in email_lower:
                return True

        return False

    def extract_name(self, from_header):
        """Extract name from From header"""
        match = re.search(r'["\']?(.+?)["\']?\s*<', from_header)
        if match:
            return match.group(1).strip()
        return from_header.split('@')[0] if '@' in from_header else from_header

    def extract_phone(self, msg):
        """Extract phone number from email body"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,15}'
        ]

        # Check in email body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    for pattern in phone_patterns:
                        match = re.search(pattern, body)
                        if match:
                            return match.group(0)

        return ''

    def extract_cv_from_email(self, msg):
        """Extract and parse CV from email attachments"""
        cv_data = {'text': '', 'path': ''}

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if filename:
                file_ext = os.path.splitext(filename)[1].lower()

                # Save attachment
                cv_path = f"cv_cache/{filename}"
                os.makedirs('cv_cache', exist_ok=True)

                with open(cv_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                # Parse based on file type
                if file_ext == '.pdf':
                    cv_data['text'] = self.parse_pdf(cv_path)
                    cv_data['path'] = cv_path
                elif file_ext in ['.docx', '.doc']:
                    cv_data['text'] = self.parse_docx(cv_path)
                    cv_data['path'] = cv_path
                elif file_ext == '.txt':
                    with open(cv_path, 'r', encoding='utf-8', errors='ignore') as f:
                        cv_data['text'] = f.read()
                    cv_data['path'] = cv_path

                if cv_data['text']:
                    logger.info(f"Extracted CV: {filename} ({len(cv_data['text'])} chars)")
                    break

        return cv_data

    def parse_pdf(self, path):
        """Parse text from PDF file"""
        if not CV_PARSING_AVAILABLE:
            return ''

        try:
            with open(path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                text = ''
                for page in pdf.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return ''

    def parse_docx(self, path):
        """Parse text from DOCX file"""
        if not CV_PARSING_AVAILABLE:
            return ''

        try:
            doc = docx.Document(path)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return ''

    def score_candidate(self, candidate_data):
        """Score candidate based on requirements"""
        score = 0
        max_score = self.config.get('scoring', {}).get('max_score', 10)
        feedback = []

        cv_text = candidate_data.get('cv_content', '').lower()

        # Required Skills (0-3 points)
        required_skills = self.requirements.get('required_skills', [])
        matched_required = sum(1 for skill in required_skills if skill.lower() in cv_text)
        if required_skills:
            skill_score = min(3, int((matched_required / len(required_skills)) * 3))
            score += skill_score
            feedback.append(f"Required Skills: {matched_required}/{len(required_skills)} matched")

        # Preferred Skills (0-2 points)
        preferred_skills = self.requirements.get('preferred_skills', [])
        matched_preferred = sum(1 for skill in preferred_skills if skill.lower() in cv_text)
        if preferred_skills:
            pref_score = min(2, int((matched_preferred / len(preferred_skills)) * 2))
            score += pref_score
            feedback.append(f"Preferred Skills: {matched_preferred}/{len(preferred_skills)} matched")

        # Experience (0-2 points)
        min_experience = self.requirements.get('min_experience', 0)
        if min_experience > 0:
            # Try to extract years of experience
            exp_match = re.search(r'(\d+)\+?\s*years?', cv_text)
            if exp_match:
                years = int(exp_match.group(1))
                if years >= min_experience:
                    score += 2
                    feedback.append(f"Experience: {years} years (meets requirement)")
                elif years >= min_experience - 1:
                    score += 1
                    feedback.append(f"Experience: {years} years (close)")
                else:
                    feedback.append(f"Experience: {years} years (below requirement)")
            else:
                feedback.append("Experience: Could not determine")
        else:
            score += 2  # Full points if no requirement

        # Education (0-1 point)
        education = self.requirements.get('education', [])
        if education:
            edu_match = any(e.lower() in cv_text for e in education)
            if edu_match:
                score += 1
                feedback.append(f"Education: Match found")
            else:
                feedback.append(f"Education: No clear match")
        else:
            score += 1  # Full points if no requirement

        # Keywords (0-2 points)
        keywords = self.requirements.get('keywords', [])
        matched_keywords = sum(1 for kw in keywords if kw.lower() in cv_text)
        if keywords:
            keyword_score = min(2, int((matched_keywords / len(keywords)) * 2))
            score += keyword_score
            feedback.append(f"Keywords: {matched_keywords}/{len(keywords)} matched")

        # Cap at max score
        score = min(score, max_score)

        return {
            'score': score,
            'feedback': '; '.join(feedback),
            'status': 'Passed' if score >= self.config.get('scoring', {}).get('passing_score', 8) else 'Review'
        }

    def send_whatsapp_notification(self, candidate_data):
        """Send WhatsApp notification for high-scoring candidate"""
        if not self.whatsapp_handler:
            logger.warning("WhatsApp handler not configured")
            return

        message = f"""🎉 *High-Scoring Candidate Alert!*

*Name:* {candidate_data['name']}
*Email:* {candidate_data['email']}
*Phone:* {candidate_data.get('phone', 'N/A')}
*Position:* {candidate_data['position']}
*Score:* {candidate_data['score']}/10

*Feedback:*
{candidate_data['feedback']}

*Time:* {candidate_data['timestamp']}

📧 CV has been saved. Consider scheduling an interview!"""

        self.whatsapp_handler.send_message(message)
        logger.info(f"WhatsApp notification sent for {candidate_data['name']}")

    def send_auto_reply(self, candidate_data):
        """Send automatic reply email to candidate"""
        if not self.email_handler:
            logger.warning("Email handler not configured")
            return False

        auto_reply_config = self.config.get('auto_reply', {})
        company_name = auto_reply_config.get('company_name', 'SKILL AI')
        interview_days = auto_reply_config.get('interview_days', 3)
        position = candidate_data.get('position', 'Software Engineer')
        recipient_email = candidate_data.get('email', '')

        logger.info(f"Preparing auto-reply for: {recipient_email} (Name: {candidate_data.get('name', 'Unknown')})")

        if not recipient_email:
            logger.error("No recipient email found in candidate_data. Cannot send auto-reply.")
            return False

        subject = f"Application Received - {position} | {company_name}"
        body = f"""Dear {candidate_data['name']},

Thank you for applying for the {position} role at {company_name}.

We have received your application and it is currently under review. If your profile matches our requirements, you can expect to receive an interview call within {interview_days} days.

We appreciate your interest in joining our team!

Best regards,
HR Team
{company_name}
"""

        success = self.email_handler.send_email(recipient_email, subject, body)
        if success:
            logger.info(f"Auto-reply sent successfully to {recipient_email}")
        else:
            logger.error(f"Failed to send auto-reply to {recipient_email}")
        return success

    def start(self):
        """Start the monitoring loop (runs once and exits)"""
        logger.info("="*60)
        logger.info("JOB APPLICATION MONITOR STARTED")
        logger.info("="*60)

        try:
            mail = self.connect_email()
            if mail:
                self.process_new_emails(mail)
                mail.close()
                mail.logout()
                logger.info("Email processing completed. Monitor stopped.")
            else:
                logger.error("Failed to connect to email server.")
        except Exception as e:
            logger.error(f"Error: {e}")

        logger.info("="*60)
        logger.info("MONITOR FINISHED")
        logger.info("="*60)


class GoogleSheetsHandler:
    """Handler for Google Sheets operations"""

    def __init__(self, config):
        self.config = config
        self.service = None
        self.spreadsheet_id = config.get('spreadsheet_id', '')
        self.sheet_name = config.get('sheet_name', 'Applications')

        if GOOGLE_SHEETS_AVAILABLE and self.spreadsheet_id:
            self.initialize_service()

    def initialize_service(self):
        """Initialize Google Sheets service"""
        try:
            credentials_file = self.config.get('credentials_file', 'credentials.json')

            if not os.path.exists(credentials_file):
                logger.warning(f"Google Sheets credentials file not found: {credentials_file}")
                return

            credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

            self.service = build('sheets', 'v4', credentials=credentials)
            self.setup_sheet()
            logger.info("Google Sheets handler initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")

    def setup_sheet(self):
        """Setup the sheet with headers if not exists"""
        try:
            # Check if sheet has data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A1:L1'
            ).execute()

            if not result.get('values'):
                # Add headers
                headers = [
                    'Timestamp', 'Name', 'Email', 'Phone', 'Position',
                    'Score', 'Feedback', 'Status', 'CV Path', 'Subject'
                ]
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f'{self.sheet_name}!A1:L1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                logger.info("Sheet headers created")

        except Exception as e:
            logger.error(f"Error setting up sheet: {e}")

    def add_candidate(self, candidate_data):
        """Add candidate to Google Sheets"""
        try:
            row = [
                candidate_data.get('timestamp', ''),
                candidate_data.get('name', ''),
                candidate_data.get('email', ''),
                candidate_data.get('phone', ''),
                candidate_data.get('position', ''),
                candidate_data.get('score', ''),
                candidate_data.get('feedback', ''),
                candidate_data.get('status', ''),
                candidate_data.get('cv_path', ''),
                candidate_data.get('subject', '')
            ]

            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:L',
                valueInputOption='RAW',
                body={'values': [row]}
            ).execute()

            logger.info(f"Candidate added to Google Sheets: {candidate_data['name']}")

        except Exception as e:
            logger.error(f"Error adding to Google Sheets: {e}")
            # Fallback to CSV backup
            self._save_to_csv(candidate_data)

    def _save_to_csv(self, candidate_data):
        """Save candidate to CSV file as backup"""
        try:
            import csv

            csv_file = 'applications_backup.csv'
            file_exists = os.path.exists(csv_file)

            row = [
                candidate_data.get('timestamp', ''),
                candidate_data.get('name', ''),
                candidate_data.get('email', ''),
                candidate_data.get('phone', ''),
                candidate_data.get('position', ''),
                candidate_data.get('score', ''),
                candidate_data.get('feedback', ''),
                candidate_data.get('status', ''),
                candidate_data.get('cv_path', ''),
                candidate_data.get('subject', '')
            ]

            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Write headers if file is new
                    writer.writerow([
                        'Timestamp', 'Name', 'Email', 'Phone', 'Position',
                        'Score', 'Feedback', 'Status', 'CV Path', 'Subject'
                    ])
                writer.writerow(row)

            logger.info(f"Candidate saved to CSV backup: {csv_file}")

        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")


class WhatsAppHandler:
    """Handler for WhatsApp notifications via Twilio"""

    def __init__(self, config):
        self.config = config
        self.client = None

        if TWILIO_AVAILABLE:
            account_sid = config.get('account_sid')
            auth_token = config.get('auth_token')
            if account_sid and auth_token:
                self.client = Client(account_sid, auth_token)
                logger.info("WhatsApp handler initialized")

    def send_message(self, message):
        """Send WhatsApp message"""
        try:
            from_number = self.config.get('from_number')
            to_number = self.config.get('to_number')

            if not all([from_number, to_number]):
                logger.warning("WhatsApp numbers not configured")
                return

            self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            logger.info("WhatsApp message sent")

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")


class EmailHandler:
    """Handler for sending emails"""

    def __init__(self, config):
        self.config = config

    def send_email(self, to_email, subject, body):
        """Send email using SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            sender_email = self.config.get('email_address')
            app_password = self.config.get('app_password')

            if not sender_email or not app_password:
                logger.warning("Email credentials not configured")
                return False

            # Validate recipient email before sending
            if not to_email or '@' not in to_email:
                logger.error(f"Invalid recipient email: '{to_email}'. Cannot send email.")
                return False

            logger.info(f"Preparing email: FROM={sender_email} TO={to_email} SUBJECT={subject}")

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            logger.info(f"Sending email to: {to_email}")

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()

            logger.info(f"Email successfully sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False


def main():
    """Main entry point"""
    monitor = JobApplicationMonitor()
    monitor.start()


if __name__ == "__main__":
    main()
