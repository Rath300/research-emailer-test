#!/usr/bin/env python3
"""
🔒 Secure Setup Script for AI Cold Outreach System
Helps configure the system without exposing API keys in git
"""

import os
import sys
import json
from pathlib import Path

def main():
    print("🔒 Secure AI Cold Outreach System Setup")
    print("=" * 50)
    
    # Check if local_config.py already exists
    if os.path.exists('local_config.py'):
        print("✅ local_config.py already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 Configuration Setup")
    print("This will create a local_config.py file that is automatically gitignored.")
    print("Your API key will be stored securely and never committed to git.")
    print()
    
    # Get OpenAI API Key
    api_key = input("Enter your OpenAI API Key (starts with sk-): ").strip()
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return
    
    # Get user profile
    print("\n👤 User Profile Setup")
    user_name = input("Your name (default: AI Developer): ").strip() or "AI Developer"
    user_email = input("Your email (default: developer@example.com): ").strip() or "developer@example.com"
    
    print("\n🛠️ Skills (comma-separated)")
    skills_input = input("Your skills (default: Python,Machine Learning,Web Development): ").strip()
    skills = [s.strip() for s in (skills_input or "Python,Machine Learning,Web Development").split(',')]
    
    experience = input("Experience (default: 5+ years in AI and software development): ").strip() or "5+ years in AI and software development"
    
    # Create local_config.py
    config_content = f'''# LOCAL DEVELOPMENT CONFIG - NEVER COMMIT TO GIT!
# This file is automatically ignored by .gitignore

OPENAI_API_KEY = "{api_key}"
USE_REAL_AI = True

# User Profile
USER_NAME = "{user_name}"
USER_EMAIL = "{user_email}"
USER_SKILLS = {skills}
USER_EXPERIENCE = "{experience}"

# Email Configuration (optional - for real email sending)
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# EMAIL_USER = "your-email@gmail.com"
# EMAIL_PASSWORD = "your-app-password"
'''
    
    try:
        with open('local_config.py', 'w') as f:
            f.write(config_content)
        
        print("\n✅ Configuration saved successfully!")
        print("📁 Created: local_config.py (gitignored)")
        
        # Verify .gitignore exists
        if not os.path.exists('.gitignore'):
            print("⚠️ Warning: .gitignore not found. Creating one...")
            with open('.gitignore', 'w') as f:
                f.write("local_config.py\n*.env\napi_keys.txt\nuploads/\n")
        
        # Test configuration
        print("\n🧪 Testing configuration...")
        try:
            from secure_config import CONFIG, is_secure
            if CONFIG['OPENAI_API_KEY'] == api_key:
                print("✅ Configuration loaded successfully!")
                print(f"🔒 Security Status: {'✅ SECURE' if is_secure() else '⚠️ INSECURE'}")
            else:
                print("❌ Configuration test failed")
        except Exception as e:
            print(f"⚠️ Configuration test error: {e}")
        
        print("\n🚀 Ready to start!")
        print("Run: python secure_m1_system.py")
        print("Open: http://localhost:5001")
        
        print("\n🛡️ Security Reminders:")
        print("- local_config.py is automatically gitignored")
        print("- Never commit API keys to git")
        print("- Rotate your API key regularly")
        print("- Read SECURITY.md for more information")
        
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return

def check_security():
    """Check current security status"""
    print("🔍 Security Check")
    print("-" * 20)
    
    # Check if sensitive files exist
    sensitive_files = ['local_config.py', '.env', 'api_keys.txt']
    for file in sensitive_files:
        if os.path.exists(file):
            print(f"📁 Found: {file}")
    
    # Check .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        protected = []
        for file in sensitive_files:
            if file in gitignore_content:
                protected.append(file)
        
        print(f"🛡️ Protected files: {', '.join(protected)}")
    else:
        print("⚠️ No .gitignore found!")
    
    # Check for exposed keys
    try:
        import subprocess
        result = subprocess.run(['grep', '-r', 'sk-', '.', '--exclude-dir=.git', '--exclude=*.md'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("⚠️ Potential exposed API keys found!")
            print("Check these files:", result.stdout)
        else:
            print("✅ No exposed API keys found")
    except:
        print("⚠️ Could not check for exposed keys")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_security()
    else:
        main() 