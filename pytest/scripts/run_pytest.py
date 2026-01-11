#!/usr/bin/env python3
"""
Run pytest with common options and parse results.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_pytest(args):
    """Execute pytest with specified options."""
    cmd = ['pytest', '-v']

    if args.coverage:
        cmd.extend(['--cov=', '--cov-report=term-missing'])

    if args.stop:
        cmd.append('-x')

    if args.last_failed:
        cmd.append('--lf')

    if args.pattern:
        cmd.extend(['-k', args.pattern])

    if args.file:
        cmd.append(args.file)

    if args.markers:
        cmd.extend(['-m', args.markers])

    if args.pdb:
        cmd.append('--pdb')

    if args.args:
        cmd.extend(args.args)

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run pytest with common options')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output (always enabled)')
    parser.add_argument('-x', '--stop', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--cov', '--coverage', action='store_true',
                       help='Run with coverage')
    parser.add_argument('--lf', '--last-failed', action='store_true',
                       help='Run last failed tests only')
    parser.add_argument('-k', '--pattern',
                       help='Run tests matching pattern')
    parser.add_argument('-f', '--file',
                       help='Run specific test file')
    parser.add_argument('-m', '--markers',
                       help='Run tests with marker')
    parser.add_argument('--pdb', action='store_true',
                       help='Drop into debugger on failure')
    parser.add_argument('args', nargs='*',
                       help='Additional pytest arguments')

    args = parser.parse_args()

    sys.exit(run_pytest(args))


if __name__ == '__main__':
    main()
