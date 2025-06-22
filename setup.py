#!/usr/bin/env python3
"""
Setup script for Cold Outreach AI Matchmaker
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_env_file():
    """Create .env file from template."""
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_NAME=Your Name
FROM_EMAIL=your_email@gmail.com
REPLY_TO=your_email@gmail.com

# Optional: Custom matching configuration
MIN_SCORE_THRESHOLD=0.6
EMAIL_TONE=confident
EMAIL_LENGTH=concise
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please edit .env file with your actual credentials")
    else:
        print("ℹ️  .env file already exists")


def main():
    """Main setup function."""
    print("🚀 Setting up Cold Outreach AI Matchmaker")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Test the system
    print("\n🧪 Testing the system...")
    if run_command("python test_system.py", "Running system tests"):
        print("✅ System tests passed")
    else:
        print("⚠️  System tests failed - this might be due to missing API keys")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your OpenAI API key and email settings")
    print("2. Customize sample_profile.json with your information")
    print("3. Add your startup database to sample_startups.csv")
    print("4. Run: python main.py match --profile sample_profile.json --startups sample_startups.csv")
    print("\nFor help, run: python main.py --help")


if __name__ == "__main__":
    main() 