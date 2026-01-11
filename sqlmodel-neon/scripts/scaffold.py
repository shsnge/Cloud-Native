#!/usr/bin/env python3
"""
FastAPI + Neon + SQLModel project scaffolding script.

Usage:
    # Create new project
    python scaffold.py new my-project

    # Add to existing project
    python scaffold.py add
"""
import argparse
import os
import shutil
import sys
from pathlib import Path


def copy_file_safe(src: Path, dst: Path) -> None:
    """Copy a file, creating parent directories if needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def create_new_project(project_name: str, target_dir: Path) -> None:
    """Create a new FastAPI project with Neon and SQLModel."""
    print(f"Creating new project: {project_name}")

    project_path = target_dir / project_name
    if project_path.exists():
        print(f"Error: Directory '{project_path}' already exists")
        sys.exit(1)

    project_path.mkdir(parents=True)

    # Get the template directory (relative to this script)
    script_dir = Path(__file__).parent.parent
    template_dir = script_dir / "assets" / "fastapi-template"

    # Copy template files
    files_to_copy = [
        ("pyproject.toml", "pyproject.toml"),
        ("database.py", "database.py"),
        ("main.py", "main.py"),
        (".env.example", ".env"),
        (".gitignore", ".gitignore"),
    ]

    for src_file, dst_file in files_to_copy:
        src = template_dir / src_file
        dst = project_path / dst_file
        copy_file_safe(src, dst)
        print(f"  Created: {dst_file}")

    # Update project name in pyproject.toml
    pyproject = project_path / "pyproject.toml"
    content = pyproject.read_text()
    content = content.replace('name = "fastapi-sqlmodel-neon"', f'name = "{project_name}"')
    pyproject.write_text(content)

    print(f"\nProject created successfully!")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  uv sync")
    print(f"  # Edit .env with your Neon connection string")
    print(f"  uv run uvicorn main:app --reload")


def add_to_existing_project(target_dir: Path) -> None:
    """Add Neon/SQLModel support to an existing project."""
    print("Adding Neon + SQLModel to existing project")

    if not (target_dir / "pyproject.toml").exists():
        print("Error: No pyproject.toml found. Are you in a UV project?")
        sys.exit(1)

    # Get the template directory
    script_dir = Path(__file__).parent.parent
    template_dir = script_dir / "assets" / "fastapi-template"

    # Copy database configuration
    copy_file_safe(template_dir / "database.py", target_dir / "database.py")
    print("  Created: database.py")

    # Add dependencies to pyproject.toml
    pyproject = target_dir / "pyproject.toml"
    content = pyproject.read_text()

    # Check if dependencies already exist
    required_deps = ['sqlmodel', 'psycopg', 'pydantic-settings']
    missing_deps = []

    for dep in required_deps:
        if dep not in content:
            missing_deps.append(dep)

    if missing_deps:
        print(f"\n  Add these dependencies to pyproject.toml:")
        print(f'  dependencies = [')
        if 'sqlmodel' in missing_deps:
            print(f'      "sqlmodel>=0.0.22",')
        if 'psycopg' in missing_deps:
            print(f'      "psycopg[binary]>=3.2.0",')
        if 'pydantic-settings' in missing_deps:
            print(f'      "pydantic-settings>=2.0.0",')
        print(f'  ]')
        print(f"\n  Then run: uv sync")

    # Update .env.example or create it
    env_example = target_dir / ".env.example"
    if env_example.exists():
        # Append Neon config to existing file
        with open(env_example, "a") as f:
            f.write("\n# Neon PostgreSQL\n")
            f.write("NEON_DATABASE_URL=\n")
        print("  Updated: .env.example")
    else:
        copy_file_safe(template_dir / ".env.example", env_example)
        print("  Created: .env.example")

    print("\nIntegration complete!")
    print("\nNext steps:")
    print("  1. Add dependencies to pyproject.toml (shown above)")
    print("  2. Run: uv sync")
    print("  3. Set NEON_DATABASE_URL in your .env file")
    print("  4. Import and use 'database.py' in your FastAPI app")


def main():
    parser = argparse.ArgumentParser(
        description="FastAPI + Neon + SQLModel project scaffolding"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # New project command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument(
        "name",
        help="Project name"
    )
    new_parser.add_argument(
        "-d", "--dir",
        type=Path,
        default=Path.cwd(),
        help="Target directory (default: current directory)"
    )

    # Add to existing project command
    add_parser = subparsers.add_parser("add", help="Add to existing project")
    add_parser.add_argument(
        "-d", "--dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    if args.command == "new":
        create_new_project(args.name, args.dir)
    elif args.command == "add":
        add_to_existing_project(args.dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
