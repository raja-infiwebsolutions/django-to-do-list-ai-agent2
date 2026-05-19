#!/usr/bin/env python
"""
Django project setup script.
Handles environment setup, dependency installation, migrations, and optional user creation.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n{'='*60}")
    print(f"➜ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed to {description.lower()}")
        return False
    print(f"✅ {description} completed successfully")
    return True

def main():
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("\n🚀 Django Todo App Setup")
    print("=" * 60)
    
    # Step 1: Install dependencies
    if not run_command(f'"{sys.executable}" -m pip install -r requirements.txt', "Install Python dependencies"):
        sys.exit(1)
    
    # Step 2: Verify Django settings
    if not run_command(f'"{sys.executable}" manage.py check', "Check Django configuration"):
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_command(f'"{sys.executable}" manage.py migrate', "Run database migrations"):
        sys.exit(1)
    
    # Step 4: Create superuser (optional)
    print(f"\n{'='*60}")
    print("🔐 Create Superuser (optional)")
    print(f"{'='*60}")
    response = input("Create a superuser account? (y/n): ").strip().lower()
    if response == 'y':
        run_command(f'"{sys.executable}" manage.py createsuperuser', "Create superuser")
    
    # Step 5: Collect static files
    if not run_command(f'"{sys.executable}" manage.py collectstatic --noinput', "Collect static files"):
        print("⚠️  Static file collection failed, but development should still work")
    
    print(f"\n{'='*60}")
    print("✅ Setup complete!")
    print(f"{'='*60}")
    print("\nTo start the development server, run:")
    print(f"  {sys.executable} manage.py runserver")
    print("\nAccess the application at:")
    print("  http://localhost:8000")
    print("  Admin: http://localhost:8000/admin")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
