#!/usr/bin/env python3
"""
Generate pytest test files from source code.
Scaffolds test files with basic structure and placeholders.
"""

import argparse
import ast
import sys
from pathlib import Path


def extract_functions(source_file):
    """Extract function/class definitions from source file."""
    with open(source_file, 'r') as f:
        tree = ast.parse(f.read(), filename=source_file)

    tests = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            tests.append({
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'doc': ast.get_docstring(node)
            })
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                    tests.append({
                        'name': f"{node.name}.{item.name}",
                        'args': [arg.arg for arg in item.args.args],
                        'doc': ast.get_docstring(item)
                    })
    return tests


def generate_test_content(module_name, functions):
    """Generate test file content."""
    lines = [
        f'"""Tests for {module_name}"""',
        'import pytest',
        ''
    ]

    for func in functions:
        lines.append('')
        if func['doc']:
            lines.append(f'def test_{func["name"].replace(".", "_")}():')
            lines.append(f'    """{func["doc"]}"""')
        else:
            lines.append(f'def test_{func["name"].replace(".", "_")}():')

        # Add test placeholder
        args = ', '.join(func['args']) if func['args'] else ''
        lines.append(f'    # TODO: implement test for {func["name"]}')
        if args:
            lines.append(f'    result = {func["name"]}({args})')
            lines.append('    assert result is not None  # Add proper assertion')
        else:
            lines.append(f'    # result = {func["name"]}()')
            lines.append('    # assert result is not None  # Add proper assertion')
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate pytest test file from source')
    parser.add_argument('source', help='Source file to generate tests for')
    parser.add_argument('--output', '-o', default='tests/',
                       help='Output directory (default: tests/)')
    parser.add_argument('--module', '-m', help='Module name for imports')

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source file '{args.source}' not found", file=sys.stderr)
        sys.exit(1)

    functions = extract_functions(source_path)
    if not functions:
        print(f"Warning: No functions found in {args.source}", file=sys.stderr)
        sys.exit(1)

    module_name = args.module or source_path.stem
    test_content = generate_test_content(module_name, functions)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    test_file = output_dir / f'test_{module_name}.py'
    with open(test_file, 'w') as f:
        f.write(test_content)

    print(f"Generated: {test_file}")
    print(f"  Functions: {len(functions)}")
    print(f"\nEdit the test file and add proper test cases.")


if __name__ == '__main__':
    main()
