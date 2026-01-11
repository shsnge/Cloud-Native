#!/usr/bin/env python3
"""
WhatsApp Setup Helper for Job Application Monitor
Guides you through setting up Twilio WhatsApp integration
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
    print("WHATSAPP SETUP HELPER (Twilio)")
    print("="*60)
    print("\nThis helper will guide you through setting up WhatsApp")
    print("notifications for high-scoring candidates (8+ score).\n")

    print("Two options available:")
    print("1. Sandbox Mode (FREE - For testing)")
    print("2. Production Mode (Paid - Real WhatsApp numbers)\n")

    choice = input("Choose option (1 or 2): ").strip()

    if choice == "1":
        setup_sandbox()
    elif choice == "2":
        setup_production()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")

def setup_sandbox():
    """Setup Twilio WhatsApp Sandbox"""
    print_step(1, "Create Twilio Account (Free)")
    print("1. Opening Twilio signup page...")
    print("2. Sign up with email or Google account")
    print("3. Verify your email\n")

    webbrowser.open("https://www.twilio.com/try-twilio")

    input("\nAfter creating account, press Enter to continue...")

    print_step(2, "Get Account Credentials")
    print("1. Opening Twilio Console...")
    print("2. Copy your Account SID and Auth Token\n")

    webbrowser.open("https://console.twilio.com/")

    account_sid = input("\nEnter your Account SID: ").strip()
    auth_token = input("Enter your Auth Token: ").strip()

    print_step(3, "Setup WhatsApp Sandbox")
    print("1. Opening WhatsApp Sandbox...")
    print("2. Join the sandbox:")
    print("   - Send 'join <keyword>' to the sandbox number")
    print("   - Keyword is shown on the page (usually: join <word>)")
    print("3. Your phone is now verified for sandbox!\n")

    webbrowser.open("https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")

    input("\nAfter joining sandbox, press Enter to continue...")

    # Get user's phone number
    print_step(4, "Enter Your Phone Number")
    print("Enter your WhatsApp number (with country code)")
    print("Example: +923001234567\n")

    to_number = input("Your WhatsApp number: ").strip()

    if not to_number.startswith('+'):
        to_number = '+' + to_number

    # Update config.json
    print_step(5, "Update Configuration")

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    with open(config_path, 'r') as f:
        config = json.load(f)

    config['whatsapp'] = {
        "service": "twilio",
        "account_sid": account_sid,
        "auth_token": auth_token,
        "from_number": "whatsapp:+14155238886",  # Twilio sandbox number
        "to_number": f"whatsapp:{to_number}"
    }

    with open(config_path, 'w') as f:
        json.dump(config, indent=2, fp=f)

    print("\n✓ config.json updated!")

    # Test WhatsApp
    print_step(6, "Test WhatsApp Connection")

    test_now = input("\nDo you want to test WhatsApp now? (yes/no): ").strip().lower()

    if test_now == 'yes':
        try:
            from twilio.rest import Client

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                from_="whatsapp:+14155238886",
                body="🎉 Job Application Monitor is now connected! You'll receive WhatsApp notifications for candidates scoring 8+.",
                to=f"whatsapp:{to_number}"
            )

            print("\n✓ Test message sent!")
            print(f"Message SID: {message.sid}")

        except ImportError:
            print("\n⚠ Twilio library not installed")
            print("Install with: pip install twilio")
        except Exception as e:
            print(f"\n⚠ Error sending test: {e}")

    print("\n" + "="*60)
    print("WHATSAPP SETUP COMPLETE!")
    print("="*60)
    print("\nSandbox Mode:")
    print(f"- From: +14155238886 (Twilio Sandbox)")
    print(f"- To: {to_number}")
    print("\nNote: Sandbox mode works for testing. For production,")
    print("you'll need a dedicated WhatsApp number from Twilio.")

def setup_production():
    """Setup Twilio WhatsApp Production"""
    print_step(1, "Create Twilio Account")
    print("1. Opening Twilio signup page...\n")

    webbrowser.open("https://www.twilio.com/try-twilio")

    input("\nAfter creating account, press Enter to continue...")

    print_step(2, "Get WhatsApp Sender Number")
    print("1. Opening Twilio WhatsApp section...")
    print("2. Get a WhatsApp sender number")
    print("   - This is a paid service")
    print("   - Costs vary by region\n")

    webbrowser.open("https://console.twilio.com/us1/develop/sms/whatsapp/learn")

    input("\nAfter getting WhatsApp number, press Enter to continue...")

    print_step(3, "Get Credentials")

    webbrowser.open("https://console.twilio.com/")

    account_sid = input("\nEnter your Account SID: ").strip()
    auth_token = input("Enter your Auth Token: ").strip()
    from_number = input("Enter your WhatsApp Sender Number (e.g., +14155238886): ").strip()
    to_number = input("Enter your personal WhatsApp number: ").strip()

    if not from_number.startswith('+'):
        from_number = '+' + from_number
    if not to_number.startswith('+'):
        to_number = '+' + to_number

    # Update config.json
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    with open(config_path, 'r') as f:
        config = json.load(f)

    config['whatsapp'] = {
        "service": "twilio",
        "account_sid": account_sid,
        "auth_token": auth_token,
        "from_number": f"whatsapp:{from_number}",
        "to_number": f"whatsapp:{to_number}"
    }

    with open(config_path, 'w') as f:
        json.dump(config, indent=2, fp=f)

    print("\n✓ config.json updated!")

    print("\n" + "="*60)
    print("WHATSAPP SETUP COMPLETE!")
    print("="*60)
    print(f"\nFrom: {from_number}")
    print(f"To: {to_number}")

if __name__ == "__main__":
    main()
