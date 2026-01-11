#!/usr/bin/env python3
"""
Generate test coverage reports using pytest-cov.
"""

import argparse
import subprocess
import sys


def generate_coverage(html=False, xml=False, term=True):
    """Generate coverage reports."""
    cmd = ['pytest', '--cov=', '--cov-report=term-missing']

    if html:
        cmd.append('--cov-report=html')
        print("HTML coverage report will be in htmlcov/index.html")

    if xml:
        cmd.append('--cov-report=xml')
        print("XML coverage report will be in coverage.xml")

    if not term:
        cmd.remove('--cov-report=term-missing')

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if html:
        print("\nOpen htmlcov/index.html in a browser to view the report.")

    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Generate test coverage reports')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--xml', action='store_true',
                       help='Generate XML report')
    parser.add_argument('--no-term', action='store_true',
                       help='Skip terminal output')

    args = parser.parse_args()

    sys.exit(generate_coverage(
        html=args.html,
        xml=args.xml,
        term=not args.no_term
    ))


if __name__ == '__main__':
    main()
