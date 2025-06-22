# 🔒 Secure AI Cold Outreach System

A secure, M1 Mac compatible AI-powered cold outreach system with real OpenAI integration and comprehensive security measures.

## 🚨 CRITICAL SECURITY NOTICE

**⚠️ Your OpenAI API key was exposed in our conversation. Please:**
1. **IMMEDIATELY** go to https://platform.openai.com/api-keys
2. **REVOKE** the exposed key: `sk-qrst1234qrst1234qrst1234qrst1234qrst1234`
3. **GENERATE** a new API key
4. **USE** the secure setup process below

## 🛡️ Security Features

- ✅ **No Hardcoded API Keys** - All keys stored in gitignored files
- ✅ **Comprehensive .gitignore** - Prevents accidental key exposure
- ✅ **Dynamic Loading** - API only loaded when secure key available
- ✅ **Graceful Fallback** - Works in demo mode without keys
- ✅ **M1 Mac Compatible** - No TensorFlow dependency issues
- ✅ **Real AI Integration** - Uses OpenAI GPT-3.5-turbo when configured

## 🚀 Quick Start (Secure)

### 1. Clone & Setup
```bash
git clone <your-repo>
cd PipelineEmail
pip install flask openai
```

### 2. Secure Configuration
```bash
python setup_secure.py
```
This will:
- Prompt for your NEW OpenAI API key
- Create `local_config.py` (automatically gitignored)
- Configure your user profile
- Test the configuration

### 3. Start the System
```bash
python secure_m1_system.py
```

### 4. Open Browser
Navigate to: http://localhost:5001

## 🔧 Manual Configuration

If you prefer manual setup:

1. **Create local_config.py** (this file is gitignored):
```python
# LOCAL DEVELOPMENT CONFIG - NEVER COMMIT TO GIT!
OPENAI_API_KEY = "your-new-api-key-here"
USE_REAL_AI = True

USER_NAME = "Your Name"
USER_EMAIL = "your-email@example.com"
USER_SKILLS = ["Python", "Machine Learning", "Web Development"]
USER_EXPERIENCE = "5+ years in AI and software development"
```

2. **Verify Security**:
```bash
python setup_secure.py check
```

## 🤖 AI Agents

The system includes 4 AI agents:

1. **🕷️ Web Scraping Agent** - Finds startups from multiple sources
2. **🎯 Semantic Matching Agent** - Uses AI to match your profile with startups
3. **✉️ Email Generation Agent** - Creates personalized outreach emails
4. **📤 Email Dispatch Agent** - Sends emails with success tracking

## 🔍 System Modes

### Real AI Mode (with OpenAI API key)
- Uses GPT-3.5-turbo for semantic matching
- Generates highly personalized emails
- Advanced reasoning for startup fit analysis

### Demo Mode (no API key)
- Enhanced simulation with realistic data
- Smart matching algorithms
- Template-based email generation

## 📊 Features

- **Multi-Source Scraping**: Y Combinator, Product Hunt, AngelList
- **AI-Powered Matching**: Semantic analysis of startup-developer fit
- **Personalized Emails**: Custom outreach based on startup details
- **Campaign Analytics**: Success rates, reports, and tracking
- **Secure by Design**: No API key exposure, comprehensive security

## 🛡️ Security Best Practices

### Before Each Git Commit:
```bash
# Check what you're committing
git status

# Verify no sensitive files
python setup_secure.py check

# Check for exposed keys
grep -r "sk-" . --exclude-dir=.git --exclude="*.md"
```

### Files That Are Gitignored:
- `local_config.py` - Your development configuration
- `.env` - Environment variables
- `uploads/` - Campaign data and reports
- `*.key` - Any API key files
- `api_keys.txt` - Key storage files

## 🚨 If You Accidentally Expose Keys

1. **Immediately revoke** the key in OpenAI dashboard
2. **Generate new key** 
3. **Update local_config.py**
4. **Clean git history** if key was committed:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch local_config.py' --prune-empty --tag-name-filter cat -- --all
   ```

## 📋 Usage Examples

### Basic Cold Outreach Campaign:
1. Open http://localhost:5001
2. Configure sources and limits
3. Deploy Web Scraping Agent
4. Deploy Semantic Matching Agent
5. Deploy Email Generation Agent
6. Review generated emails
7. Deploy Email Dispatch Agent

### Advanced Configuration:
- Customize user profile in `local_config.py`
- Add SMTP settings for real email sending
- Adjust matching criteria and thresholds

## 🔄 Updates & Maintenance

### Regular Security Tasks:
- Rotate API keys quarterly
- Update dependencies: `pip install --upgrade openai flask`
- Review and update .gitignore
- Monitor API usage and costs

### System Updates:
```bash
git pull origin main
pip install -r requirements.txt
python setup_secure.py check
```

## 📞 Support

- **Security Issues**: Read `SECURITY.md`
- **Setup Problems**: Run `python setup_secure.py check`
- **API Errors**: Verify your OpenAI API key is valid

## ⚖️ Legal & Ethical Use

- Only use for legitimate business outreach
- Respect recipient privacy and preferences
- Include unsubscribe options in emails
- Comply with CAN-SPAM and GDPR regulations
- Use responsibly and ethically

---

**Remember**: Security is paramount. When in doubt, ask for help rather than risk exposing sensitive information. 