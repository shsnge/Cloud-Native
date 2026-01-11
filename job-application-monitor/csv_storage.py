#!/usr/bin/env python3
"""
Simple CSV-based storage for job applications
Use this if you don't want to set up Google Sheets
"""

import csv
import os
from datetime import datetime


class CSVStorage:
    """Simple CSV storage for job applications"""

    def __init__(self, csv_file='applications_backup.csv'):
        self.csv_file = csv_file
        self.ensure_headers()

    def ensure_headers(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Name', 'Email', 'Phone', 'Position',
                    'Score', 'Feedback', 'Status', 'CV Path', 'Subject'
                ])
            print(f"Created {self.csv_file}")

    def add_candidate(self, candidate_data):
        """Add candidate to CSV file"""
        try:
            row = [
                candidate_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
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

            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)

            print(f"✓ Candidate saved to CSV: {candidate_data.get('name', 'Unknown')}")
            return True

        except Exception as e:
            print(f"✗ Error saving to CSV: {e}")
            return False

    def get_all_candidates(self):
        """Get all candidates from CSV"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []

    def print_summary(self):
        """Print summary of all candidates"""
        candidates = self.get_all_candidates()

        print("\n" + "="*60)
        print("JOB APPLICATIONS SUMMARY")
        print("="*60)
        print(f"Total Applications: {len(candidates)}")

        if candidates:
            print("\nRecent Applications:")
            for i, candidate in enumerate(candidates[-5:], 1):
                print(f"\n{i}. {candidate.get('Name', 'Unknown')} - {candidate.get('Position', 'N/A')}")
                print(f"   Email: {candidate.get('Email', 'N/A')}")
                print(f"   Score: {candidate.get('Score', 'N/A')}/10 | Status: {candidate.get('Status', 'N/A')}")

        print("\n" + "="*60)


if __name__ == "__main__":
    storage = CSVStorage()
    storage.print_summary()
