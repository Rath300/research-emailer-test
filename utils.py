import json
import csv
import pandas as pd
from typing import List, Dict, Optional, Union
from pathlib import Path
import yaml
from data_models import UserProfile, Startup, EmailMatch, EmailBatch, FundingStage
import os
from datetime import datetime


def load_user_profile(file_path: str) -> UserProfile:
    """Load user profile from JSON or Markdown file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Profile file not found: {file_path}")
    
    if file_path.suffix.lower() == '.json':
        return _load_json_profile(file_path)
    elif file_path.suffix.lower() in ['.md', '.markdown']:
        return _load_markdown_profile(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def _load_json_profile(file_path: Path) -> UserProfile:
    """Load user profile from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return UserProfile(**data)


def _load_markdown_profile(file_path: Path) -> UserProfile:
    """Load user profile from Markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse markdown content
    lines = content.split('\n')
    profile_data = {
        "name": "",
        "title": "",
        "email": "",
        "projects": [],
        "skills": [],
        "experience": "",
        "linkedin": None,
        "github": None
    }
    
    current_section = None
    current_project = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            profile_data["name"] = line[2:].strip()
        elif line.startswith('## '):
            section = line[3:].strip().lower()
            current_section = section
        elif line.startswith('### '):
            if current_section == 'projects':
                if current_project:
                    profile_data["projects"].append(current_project)
                current_project = {
                    "name": line[4:].strip(),
                    "description": "",
                    "tech_stack": [],
                    "outcomes": [],
                    "duration": None,
                    "role": None
                }
        elif line.startswith('- ') and current_section:
            item = line[2:].strip()
            if current_section == 'skills':
                profile_data["skills"].append(item)
            elif current_section == 'projects' and current_project:
                if 'tech' in item.lower():
                    current_project["tech_stack"].append(item)
                elif 'outcome' in item.lower() or 'result' in item.lower():
                    current_project["outcomes"].append(item)
                else:
                    current_project["description"] += " " + item
        elif line and current_section == 'experience':
            profile_data["experience"] += " " + line
        elif line and current_section == 'contact':
            if 'linkedin' in line.lower():
                profile_data["linkedin"] = line
            elif 'github' in line.lower():
                profile_data["github"] = line
            elif '@' in line:
                profile_data["email"] = line
    
    # Add the last project if exists
    if current_project:
        profile_data["projects"].append(current_project)
    
    return UserProfile(**profile_data)


def load_startups(file_path: str) -> List[Startup]:
    """Load startups from CSV file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Startups file not found: {file_path}")
    
    startups = []
    
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            # Parse tech stack
            tech_stack = []
            if 'tech_stack' in row and pd.notna(row['tech_stack']):
                tech_stack = [tech.strip() for tech in str(row['tech_stack']).split(',')]
            
            # Parse funding stage
            funding_stage = None
            if 'funding_stage' in row and pd.notna(row['funding_stage']):
                try:
                    funding_stage = FundingStage(row['funding_stage'])
                except ValueError:
                    funding_stage = FundingStage.OTHER
            
            startup_data = {
                "company_name": row.get('company_name', ''),
                "mission": row.get('mission', ''),
                "product": row.get('product', ''),
                "tech_stack": tech_stack,
                "team_size": row.get('team_size'),
                "funding_stage": funding_stage,
                "website": row.get('website'),
                "contact_email": row.get('contact_email'),
                "contact_name": row.get('contact_name'),
                "location": row.get('location'),
                "industry": row.get('industry'),
                "description": row.get('description')
            }
            
            startups.append(Startup(**startup_data))
    
    return startups


def save_email_batch(batch: EmailBatch, file_path: str) -> str:
    """Save email batch to JSON file."""
    file_path = Path(file_path)
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(batch.dict(), f, indent=2, default=str)
    
    return str(file_path)


def load_email_batch(file_path: str) -> EmailBatch:
    """Load email batch from JSON file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Email batch file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return EmailBatch(**data)


def export_matches_to_csv(matches: List[EmailMatch], file_path: str) -> str:
    """Export matches to CSV file for review."""
    file_path = Path(file_path)
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = []
    for match in matches:
        data.append({
            "company_name": match.company_name,
            "contact_email": match.contact_email,
            "contact_name": match.contact_name,
            "match_score": match.match_score,
            "tech_stack_alignment": match.rationale.tech_stack_alignment,
            "domain_alignment": match.rationale.domain_alignment,
            "project_relevance": match.rationale.project_relevance,
            "relevant_projects": ", ".join(match.relevant_projects),
            "rationale": "; ".join(match.rationale.reasoning),
            "subject_line": match.subject_line,
            "email_body": match.email_body,
            "auto_send": match.auto_send
        })
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    
    return str(file_path)


def create_sample_profile() -> UserProfile:
    """Create a sample user profile for testing."""
    return UserProfile(
        name="John Doe",
        title="Senior Software Engineer",
        email="john.doe@example.com",
        projects=[
            {
                "name": "E-commerce Platform",
                "description": "Built a scalable e-commerce platform serving 10,000+ users",
                "tech_stack": ["React", "Node.js", "PostgreSQL", "AWS"],
                "outcomes": ["50% revenue increase", "10,000+ active users"],
                "duration": "18 months",
                "role": "Lead Developer"
            },
            {
                "name": "AI Chatbot",
                "description": "Developed an AI-powered customer service chatbot",
                "tech_stack": ["Python", "TensorFlow", "FastAPI", "Docker"],
                "outcomes": ["80% customer satisfaction", "24/7 support coverage"],
                "duration": "12 months",
                "role": "ML Engineer"
            }
        ],
        skills=["JavaScript", "Python", "AWS", "Docker", "PostgreSQL", "React"],
        experience="5 years building scalable web applications and AI systems",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe"
    )


def create_sample_startups() -> List[Startup]:
    """Create sample startups for testing."""
    return [
        Startup(
            company_name="TechCorp",
            mission="Revolutionizing e-commerce with AI-powered personalization",
            product="AI-powered shopping assistant",
            tech_stack=["Python", "React", "AWS", "PostgreSQL"],
            team_size=25,
            funding_stage=FundingStage.SERIES_A,
            website="techcorp.com",
            contact_email="ceo@techcorp.com",
            contact_name="Sarah Johnson",
            location="San Francisco, CA",
            industry="E-commerce",
            description="Building the future of online shopping"
        ),
        Startup(
            company_name="DataFlow",
            mission="Making data analytics accessible to everyone",
            product="No-code data visualization platform",
            tech_stack=["Python", "JavaScript", "Docker", "Kubernetes"],
            team_size=15,
            funding_stage=FundingStage.SEED,
            website="dataflow.io",
            contact_email="founder@dataflow.io",
            contact_name="Mike Chen",
            location="New York, NY",
            industry="Data Analytics",
            description="Democratizing data science"
        ),
        Startup(
            company_name="HealthTech",
            mission="Improving healthcare through technology",
            product="Telemedicine platform",
            tech_stack=["React", "Node.js", "MongoDB", "AWS"],
            team_size=40,
            funding_stage=FundingStage.SERIES_B,
            website="healthtech.com",
            contact_email="hr@healthtech.com",
            contact_name="Dr. Emily Brown",
            location="Boston, MA",
            industry="Healthcare",
            description="Connecting patients with healthcare providers"
        )
    ]


def validate_email_config() -> Dict:
    """Validate email configuration from environment variables."""
    required_vars = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'FROM_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    return {
        "valid": len(missing_vars) == 0,
        "missing_vars": missing_vars,
        "config": {
            "smtp_host": os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            "smtp_port": os.getenv('SMTP_PORT', '587'),
            "smtp_username": os.getenv('SMTP_USERNAME'),
            "from_email": os.getenv('FROM_EMAIL'),
            "from_name": os.getenv('FROM_NAME', 'Cold Outreach AI')
        }
    }


def format_match_summary(matches: List[EmailMatch]) -> str:
    """Format a human-readable summary of matches."""
    if not matches:
        return "No matches found."
    
    summary = f"Found {len(matches)} matches:\n\n"
    
    for i, match in enumerate(matches[:10], 1):  # Show top 10
        summary += f"{i}. {match.company_name} (Score: {match.match_score:.2f})\n"
        summary += f"   Contact: {match.contact_name or 'N/A'} <{match.contact_email or 'N/A'}>\n"
        summary += f"   Projects: {', '.join(match.relevant_projects[:2])}\n"
        summary += f"   Rationale: {'; '.join(match.rationale.reasoning[:2])}\n\n"
    
    if len(matches) > 10:
        summary += f"... and {len(matches) - 10} more matches\n"
    
    avg_score = sum(match.match_score for match in matches) / len(matches)
    summary += f"\nAverage match score: {avg_score:.2f}"
    
    return summary


def create_env_template() -> str:
    """Create a template .env file."""
    return """# OpenAI Configuration
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