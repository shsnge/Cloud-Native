#!/usr/bin/env python3
"""
Google Sheets Setup Helper for Job Application Monitor
Guides you through setting up Google Sheets API and creating a spreadsheet
"""

import os
import webbrowser
import json

def print_step(step_num, title):
    """Print a formatted step header"""
    print("\n" + "="*60)
    print(f"STEP {step_num}: {title}")
    print("="*60 + "\n")

def main():
    print("\n" + "="*60)
    print("GOOGLE SHEETS SETUP HELPER")
    print("="*60)
    print("\nThis helper will guide you through setting up Google Sheets")
    print("for the Job Application Monitor.\n")

    input("Press Enter to start...")

    # Step 1: Open Google Cloud Console
    print_step(1, "Create Google Cloud Project")
    print("1. Opening Google Cloud Console in your browser...")
    print("2. Create a new project (or select existing)\n")

    webbrowser.open("https://console.cloud.google.com/projectcreate")

    input("\nAfter creating the project, press Enter to continue...")

    # Step 2: Enable Sheets API
    print_step(2, "Enable Google Sheets API")
    print("1. Opening Google Sheets API page...")
    print("2. Click 'Enable' button\n")

    project_id = input("\nEnter your Project ID (from the URL): ").strip()
    webbrowser.open(f"https://console.cloud.google.com/apis/library/sheets.googleapis.com?project={project_id}")

    input("\nAfter enabling the API, press Enter to continue...")

    # Step 3: Create Service Account
    print_step(3, "Create Service Account")
    print("1. Opening Service Accounts page...")
    print("2. Click 'Create Service Account'\n")
    print("Service Account Details:")
    print("  - Name: Job Application Monitor")
    print("  - Description: Automated job application tracking")
    print("  - Click 'Create and Continue'")
    print("  - Skip granting roles (optional)")
    print("  - Click 'Done'\n")

    webbrowser.open(f"https://console.cloud.google.com/iam-admin/serviceaccounts/create?project={project_id}")

    input("\nAfter creating the service account, press Enter to continue...")

    # Step 4: Create Key
    print_step(4, "Create Service Account Key")
    print("1. Click on your service account")
    print("2. Go to 'Keys' tab")
    print("3. Click 'Add Key' → 'Create new key'")
    print("4. Select 'JSON'")
    print("5. Click 'Create'")
    print("6. The JSON file will download automatically\n")

    webbrowser.open(f"https://console.cloud.google.com/iam-admin/serviceaccounts?project={project_id}")

    input("\nAfter downloading the credentials file, press Enter to continue...")

    # Step 5: Save credentials
    print_step(5, "Save Credentials File")
    print("\nPlease follow these steps:")
    print("1. Find the downloaded JSON file (in Downloads folder)")
    print("2. Rename it to 'credentials.json'")
    print("3. Move it to this folder:\n")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"   {current_dir}\n")

    print("Or, you can:")
    print("- Copy the contents of the downloaded JSON file")
    print("- I'll create the credentials.json for you\n")

    create_now = input("Have you moved the file? (yes/no): ").strip().lower()

    if create_now != 'yes':
        print("\nOpening the file location...")
        webbrowser.open(current_dir)
        input("\nMove credentials.json here and press Enter...")

    # Check if credentials file exists
    creds_path = os.path.join(current_dir, "credentials.json")
    if os.path.exists(creds_path):
        print("\n✓ credentials.json found!")

        # Extract service account email
        with open(creds_path, 'r') as f:
            creds = json.load(f)
            sa_email = creds.get('client_email', '')
            print(f"\nYour Service Account Email: {sa_email}")
            print("\nIMPORTANT: Copy this email - you'll need it to share the Google Sheet")

    else:
        print("\n⚠ credentials.json not found!")
        print("Please move the file to continue.")

    # Step 6: Create Google Sheet
    print_step(6, "Create Google Sheet")
    print("\n1. Opening Google Sheets...")
    print("2. Create a new spreadsheet")
    print("3. Name it 'Job Applications'\n")

    webbrowser.open("https://sheets.google.com/create")

    input("\nAfter creating the sheet, press Enter to continue...")

    # Step 7: Share with Service Account
    print_step(7, "Share Sheet with Service Account")
    print("\n1. In your Google Sheet, click 'Share'")
    print("2. Paste the service account email:")
    if os.path.exists(creds_path):
        print(f"   {sa_email}")
    print("3. Set permission to 'Editor'")
    print("4. Click 'Send'\n")

    input("\nAfter sharing the sheet, press Enter to continue...")

    # Step 8: Get Spreadsheet ID
    print_step(8, "Get Spreadsheet ID")
    print("\n1. Your spreadsheet URL looks like:")
    print("   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit")
    print("2. Copy the SPREADSHEET_ID (the long string between /d/ and /edit)\n")

    spreadsheet_id = input("Enter the Spreadsheet ID: ").strip()

    if spreadsheet_id:
        # Update config.json
        config_path = os.path.join(current_dir, "config.json")

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

            config['google_sheets']['spreadsheet_id'] = spreadsheet_id

            with open(config_path, 'w') as f:
                json.dump(config, indent=2, fp=f)

            print("\n✓ config.json updated with Spreadsheet ID!")

    # Final summary
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nYour Google Sheets integration is now ready!")
    print("\nNext steps:")
    print("1. Edit requirements.json with your job requirements")
    print("2. Run the monitor: python monitor.py")
    print("\nNew applications will be automatically added to your sheet!")

if __name__ == "__main__":
    main()
