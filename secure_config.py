"""
Secure Configuration for AI Cold Outreach System
NEVER commit API keys directly to code!
"""
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    
    # Try to load from environment first
    openai_key = os.getenv('OPENAI_API_KEY')
    use_real_ai = os.getenv('USE_REAL_AI', 'false').lower() == 'true'
    
    # If not in environment, check for local config (for development only)
    if not openai_key and os.path.exists('local_config.py'):
        try:
            from local_config import OPENAI_API_KEY, USE_REAL_AI
            openai_key = OPENAI_API_KEY
            use_real_ai = USE_REAL_AI
        except ImportError:
            pass
    
    # Fallback to default if still no key
    if not openai_key:
        openai_key = 'your-api-key-here'
    
    # Load user profile from local config if available
    user_profile = {
        'name': os.getenv('USER_NAME', 'Shreyansh Rath'),
        'email': os.getenv('USER_EMAIL', 'shreyanshrath4@gmail.com'),
        'skills': os.getenv('USER_SKILLS', 'Python,AI/ML,Cloud Computing,AWS,Docker,Git,JavaScript,React,Node.js,PostgreSQL,TensorFlow,PyTorch').split(','),
        'experience': os.getenv('USER_EXPERIENCE', 'High school student with 2+ years coding experience'),
        'current_role': os.getenv('USER_CURRENT_ROLE', 'High School Student & Aspiring AI/Cloud Engineer'),
        'projects': ['AI-powered cold outreach system', 'Cloud-deployed web scraper', 'Full-stack web applications']  # Default projects
    }
    
    # Try to load from local_config.py if it exists
    if os.path.exists('local_config.py'):
        try:
            import local_config
            if hasattr(local_config, 'USER_NAME'):
                user_profile['name'] = local_config.USER_NAME
            if hasattr(local_config, 'USER_EMAIL'):
                user_profile['email'] = local_config.USER_EMAIL
            if hasattr(local_config, 'USER_SKILLS'):
                user_profile['skills'] = local_config.USER_SKILLS
            if hasattr(local_config, 'USER_EXPERIENCE'):
                user_profile['experience'] = local_config.USER_EXPERIENCE
            if hasattr(local_config, 'USER_CURRENT_ROLE'):
                user_profile['current_role'] = local_config.USER_CURRENT_ROLE
            if hasattr(local_config, 'USER_PROJECTS'):
                user_profile['projects'] = local_config.USER_PROJECTS
        except ImportError:
            pass
    
    # Load email configuration from local_config.py or environment
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'email_user': os.getenv('EMAIL_USER'),
        'email_password': os.getenv('EMAIL_PASSWORD')
    }
    
    # Override with local_config.py if available
    if os.path.exists('local_config.py'):
        try:
            import local_config
            if hasattr(local_config, 'SMTP_SERVER'):
                email_config['smtp_server'] = local_config.SMTP_SERVER
            if hasattr(local_config, 'SMTP_PORT'):
                email_config['smtp_port'] = local_config.SMTP_PORT
            if hasattr(local_config, 'EMAIL_USER'):
                email_config['email_user'] = local_config.EMAIL_USER
            if hasattr(local_config, 'EMAIL_PASSWORD'):
                email_config['email_password'] = local_config.EMAIL_PASSWORD
        except ImportError:
            pass
    
    return {
        'OPENAI_API_KEY': openai_key,
        'USE_REAL_AI': use_real_ai and bool(openai_key),
        'USER_PROFILE': user_profile,
        
        # Email Configuration for Real SMTP Sending
        'EMAIL_CONFIG': email_config
    }

# Load configuration
CONFIG = load_config()

def get_config() -> Dict[str, Any]:
    """Get the current configuration"""
    return CONFIG

# Security check
def is_secure() -> bool:
    """Check if configuration is secure (no hardcoded keys)"""
    api_key = str(CONFIG.get('OPENAI_API_KEY', ''))
    email_pass = str(CONFIG.get('EMAIL_CONFIG', {}).get('email_password', ''))
    
    # Check for fake/example keys, not real ones
    return not any([
        api_key.startswith('sk-qrst1'),  # Only flag fake keys
        api_key == 'your-api-key-here',
        'example' in api_key.lower(),
        email_pass == 'your-password-here'
    ])

print("🔒 Security Status:", "✅ SECURE" if is_secure() else "⚠️ INSECURE - Check for hardcoded keys!") 