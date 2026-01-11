#!/usr/bin/env python3
"""
Create Google Sheet for Job Application Monitor
Run this after setting up credentials.json to create the spreadsheet automatically
"""

import os
import json
import sys

def create_spreadsheet():
    """Create a new Google Sheet for job applications"""

    try:
        from googleapiclient.discovery import build
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Error: Google Sheets libraries not installed")
        print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)

    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found!")
        print("\nPlease run: python setup_sheets.py")
        print("This will guide you through setting up Google Sheets API")
        sys.exit(1)

    # Load credentials
    try:
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)

    except Exception as e:
        print(f"Error loading credentials: {e}")
        print("\nMake sure credentials.json is valid")
        sys.exit(1)

    # Create spreadsheet
    print("Creating Google Sheet...")

    spreadsheet_body = {
        'properties': {
            'title': 'Job Applications - Job Application Monitor'
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Applications'
                }
            }
        ]
    }

    try:
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()

        spreadsheet_id = spreadsheet['spreadsheetId']
        spreadsheet_url = spreadsheet['spreadsheetUrl']

        print(f"\n✓ Google Sheet created successfully!")
        print(f"\nSpreadsheet ID: {spreadsheet_id}")
        print(f"URL: {spreadsheet_url}")

        # Add headers
        headers = [
            'Timestamp', 'Name', 'Email', 'Phone', 'Position',
            'Score', 'Feedback', 'Status', 'CV Path', 'Subject'
        ]

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Applications!A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()

        print("\n✓ Headers added to the sheet")

        # Update config.json
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)

            config['google_sheets']['spreadsheet_id'] = spreadsheet_id

            with open('config.json', 'w') as f:
                json.dump(config, indent=2, fp=f)

            print("\n✓ config.json updated with Spreadsheet ID")

        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print("\nYour Google Sheet is ready!")
        print("New job applications will be automatically added here.")
        print(f"\nView your sheet: {spreadsheet_url}")

        # Open the sheet in browser
        import webbrowser
        webbrowser.open(spreadsheet_url)

    except Exception as e:
        print(f"\nError creating spreadsheet: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_spreadsheet()
