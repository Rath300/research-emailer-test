# 📧 Email Setup Guide - Real SMTP Configuration

## 🚀 **Current Status: FULLY FUNCTIONAL**

Your AI Cold Outreach system is now **100% functional** with both simulation and real email capabilities!

## 📍 **System Access**
- **Main Dashboard**: http://localhost:5001
- **Resume Upload**: http://localhost:5001/upload-resume

---

## 🔧 **Enable Real Email Sending**

### **Option 1: Environment Variables (Recommended for Production)**

Set these environment variables:

```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

### **Option 2: Local Configuration (Development)**

Add to your `local_config.py`:

```python
# Email Configuration
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

---

## 📧 **Gmail Setup (Most Common)**

### **Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Enable 2-Factor Authentication

### **Step 2: Generate App Password**
1. Go to Google Account → Security → App passwords
2. Generate a new app password for "Mail"
3. Use this 16-character password (not your regular password)

### **Step 3: Configure System**
```bash
export EMAIL_USER="yourname@gmail.com"
export EMAIL_PASSWORD="abcd efgh ijkl mnop"  # Your 16-char app password
```

---

## 🔧 **Other Email Providers**

### **Outlook/Hotmail**
```bash
export SMTP_SERVER="smtp-mail.outlook.com"
export SMTP_PORT="587"
export EMAIL_USER="your-email@outlook.com"
export EMAIL_PASSWORD="your-password"
```

### **Yahoo Mail**
```bash
export SMTP_SERVER="smtp.mail.yahoo.com"
export SMTP_PORT="587"
export EMAIL_USER="your-email@yahoo.com"
export EMAIL_PASSWORD="your-app-password"
```

### **Custom SMTP Server**
```bash
export SMTP_SERVER="your-smtp-server.com"
export SMTP_PORT="587"
export EMAIL_USER="your-email@domain.com"
export EMAIL_PASSWORD="your-password"
```

---

## ✅ **System Features**

### **Current Mode: Simulation + Real Email Ready**
- ✅ **Web Scraping**: Multi-source startup discovery
- ✅ **AI Matching**: OpenAI-powered or enhanced demo matching
- ✅ **Email Generation**: AI-powered or professional templates
- ✅ **Email Dispatch**: Real SMTP + Professional simulation
- ✅ **Resume Upload**: AI-powered profile extraction
- ✅ **Campaign Analytics**: Comprehensive reporting

### **What Emails Are Sent From**
- **From Address**: The email you configure in `EMAIL_USER`
- **SMTP Server**: Gmail, Outlook, Yahoo, or custom server
- **Authentication**: Secure app passwords or OAuth

---

## 🧪 **Testing the System**

### **1. Test Web Interface**
Visit: http://localhost:5001

### **2. Test Resume Upload**
Visit: http://localhost:5001/upload-resume

### **3. Test API Endpoints**
```bash
# Test scraping
curl -X POST http://localhost:5001/api/outreach/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["ycombinator"], "limit": 5}'

# Test matching
curl -X POST http://localhost:5001/api/outreach/match \
  -H "Content-Type: application/json" \
  -d '{"match_count": 3}'
```

---

## 🔒 **Security Notes**

### **✅ What's Secure**
- No hardcoded API keys in source code
- Environment variable configuration
- Secure file handling
- Automatic cleanup of uploaded files
- GDPR-compliant data handling

### **⚠️ Important Security Tips**
1. **Never commit email passwords to Git**
2. **Use app passwords, not regular passwords**
3. **Keep your OpenAI API key secure**
4. **Regularly rotate credentials**

---

## 🎯 **Production Deployment**

### **For Production Use:**
1. Set all environment variables
2. Use a production WSGI server (not Flask dev server)
3. Configure proper logging
4. Set up monitoring
5. Use secure SSL/TLS

### **Example Production Start:**
```bash
export OPENAI_API_KEY="your-openai-key"
export EMAIL_USER="outreach@yourcompany.com"
export EMAIL_PASSWORD="your-app-password"
export USE_REAL_AI="true"

python final_secure_system.py
```

---

## 🆘 **Troubleshooting**

### **Email Not Sending?**
1. Check your app password (not regular password)
2. Verify SMTP settings
3. Check firewall/network restrictions
4. Look at console logs for error messages

### **OpenAI API Issues?**
1. Verify API key is valid
2. Check API quota and billing
3. Ensure proper format (starts with 'sk-')

### **Resume Upload Issues?**
1. Use .txt files only
2. Check file size (max 16MB)
3. Ensure proper text encoding

---

## 🎉 **You're Ready!**

Your AI Cold Outreach system is **fully functional** and ready for:
- ✅ Professional cold outreach campaigns
- ✅ AI-powered startup matching
- ✅ Personalized email generation
- ✅ Real email sending (when configured)
- ✅ Resume-based profile extraction
- ✅ Comprehensive analytics

**Start using it now at: http://localhost:5001** 