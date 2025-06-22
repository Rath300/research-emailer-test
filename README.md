# Cold Outreach AI Matchmaker

A comprehensive AI-powered system for automating cold email outreach to early-stage startups. The system uses semantic similarity and contextual analysis to match your professional profile with relevant companies, then generates personalized emails for effective outreach.

## 🌟 Features

### Core Functionality
- **AI-Powered Matching**: Semantic similarity analysis using sentence transformers
- **Personalized Email Generation**: GPT-3.5-turbo powered emails with fallback templates
- **Smart Email Dispatch**: SMTP integration with batch sending capabilities
- **Comprehensive Analytics**: Match scoring and outreach performance tracking

### Web Dashboard
- **Modern UI**: Beautiful, responsive Bootstrap-based interface
- **Interactive Workflow**: Step-by-step guided process
- **Real-time Matching**: Live progress tracking and results
- **Email Management**: Preview, edit, and send emails with ease
- **Data Export**: CSV and JSON export capabilities
- **Configuration Management**: Easy setup for email and API settings

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (optional, for AI-generated emails)
- SMTP credentials (for sending emails)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PipelineEmail
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   export EMAIL_ADDRESS="your@email.com"
   export EMAIL_PASSWORD="your-app-password"
   ```

## 📱 Web Dashboard

The web dashboard provides a user-friendly interface for the entire cold outreach process.

### Starting the Dashboard
```bash
python run_dashboard.py
```

Then open your browser and go to: **http://localhost:5000**

### Dashboard Workflow

1. **Setup Profile** (`/profile`)
   - Enter your professional information
   - Add your experience and skills
   - Include social media links

2. **Add Projects** (`/projects`)
   - Add your key projects with descriptions
   - Specify tech stacks and outcomes
   - Include your role and duration

3. **Upload Startups** (`/startups`)
   - Upload a CSV file with startup data
   - Required columns: `company_name`, `mission`, `tech_stack`, `contact_name`, `contact_email`
   - Optional columns: `website`, `location`, `funding_stage`, `team_size`

4. **Configure Matching** (`/match`)
   - Set minimum score threshold (0.1-1.0)
   - Choose email tone (confident, professional, casual)
   - Select email length (concise, detailed, brief)
   - Enable auto-send for high-scoring matches

5. **Run Matching** (`/match`)
   - Click "Start Matching" to run AI analysis
   - View real-time progress and results
   - See match scores and rationales

6. **Manage Emails** (`/emails`)
   - Review generated emails
   - Preview and edit content
   - Select emails to send
   - Configure SMTP settings

7. **View Analytics** (`/analytics`)
   - Match distribution analysis
   - Component score breakdown
   - Top matching companies

8. **Settings** (`/settings`)
   - Configure email settings
   - Manage API keys
   - Data management options

## 💻 Command Line Interface

For advanced users, the system also provides a CLI interface:

```bash
# Basic usage
python main.py match --profile sample_profile.json --startups sample_startups.csv

# With custom configuration
python main.py match \
    --profile my_profile.json \
    --startups my_startups.csv \
    --threshold 0.7 \
    --tone professional \
    --length concise \
    --output results.json

# Send emails
python main.py send --batch results.json --auto-send
```

## 📊 Data Formats

### User Profile (JSON)
```json
{
    "name": "John Doe",
    "title": "Senior Software Engineer",
    "email": "john@example.com",
    "experience": "5+ years building scalable web applications...",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "projects": [
        {
            "name": "E-commerce Platform",
            "description": "Built a high-traffic e-commerce platform...",
            "tech_stack": ["React", "Node.js", "PostgreSQL"],
            "outcomes": ["50% revenue increase", "10,000+ users"],
            "duration": "12 months",
            "role": "Lead Developer"
        }
    ],
    "skills": ["Python", "JavaScript", "AWS", "Docker"]
}
```

### Startup Database (CSV)
```csv
company_name,mission,tech_stack,contact_name,contact_email,website,location,funding_stage,team_size
TechFlow,AI-powered workflow automation,Python React AWS,John Smith,john@techflow.com,https://techflow.com,San Francisco,Series A,15
DataViz,Real-time data visualization,JavaScript D3.js Node.js,Sarah Johnson,sarah@dataviz.com,https://dataviz.com,New York,Seed,8
```

## 🔧 Configuration

### Email Settings
Configure your SMTP settings in the web dashboard or via environment variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_ADDRESS="your@email.com"
export EMAIL_PASSWORD="your-app-password"
```

### OpenAI API (Optional)
For AI-generated emails, set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

## 📈 Analytics & Insights

The system provides comprehensive analytics:

- **Match Distribution**: High/Medium/Low quality matches
- **Component Scores**: Tech stack, domain, and project alignment
- **Email Performance**: Open rates, response rates, and engagement
- **Trend Analysis**: Matching patterns over time

## 🛠️ Development

### Project Structure
```
PipelineEmail/
├── web_dashboard.py          # Flask web application
├── main.py                   # CLI interface
├── data_models.py           # Pydantic data models
├── matcher.py               # Semantic matching engine
├── email_generator.py       # AI email generation
├── email_dispatcher.py      # SMTP email sending
├── utils.py                 # Utility functions
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── profile.html
│   ├── projects.html
│   ├── startups.html
│   ├── match.html
│   ├── emails.html
│   └── settings.html
├── static/                  # CSS, JS, and assets
│   ├── css/style.css
│   └── js/main.js
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests
```bash
python test_system.py
```

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [DOCUMENTATION.md](DOCUMENTATION.md) file
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join our community discussions

## 🚀 Roadmap

### Planned Features
- [ ] Advanced analytics dashboard
- [ ] Email template library
- [ ] Follow-up automation
- [ ] CRM integration
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Team collaboration features
- [ ] Advanced AI models integration

### Performance Improvements
- [ ] Caching layer for faster matching
- [ ] Database optimization
- [ ] Async email processing
- [ ] CDN integration for static assets

---

**Made with ❤️ for the startup community** 