#!/usr/bin/env python3
"""
Cold Outreach AI Matchmaker - Simple Web Dashboard

A lightweight web interface that starts without heavy ML imports.
"""

import os
import json
import warnings
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Suppress all warnings
warnings.filterwarnings('ignore')

# Suppress TensorFlow warnings that can cause issues
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
warnings.filterwarnings('ignore', category=FutureWarning, module='tensorflow')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Optional as OptionalValidator
from werkzeug.utils import secure_filename

# Import the scraper (if it exists and is safe to import)
try:
    from web_scraper import WebScraper, StartupData
    SCRAPER_ENABLED = True
except ImportError:
    SCRAPER_ENABLED = False

from matcher import SemanticMatcher
from email_generator import EmailGenerator
from email_dispatcher import EmailDispatcher
import logging
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for session management
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Import Real AI Agents
try:
    from ai_agents import (
        create_real_ai_agents, 
        USE_REAL_AI, 
        OPENAI_API_KEY,
        StartupData
    )
    REAL_AI_AVAILABLE = True
    logger.info("✅ Real AI agents imported successfully")
except ImportError as e:
    REAL_AI_AVAILABLE = False
    logger.warning(f"⚠️  Real AI agents not available: {e}")

# Mock AI Agents (fallback when real AI is not available)
class MockWebScrapingAgent:
    """Mock AI Agent for Web Scraping"""
    
    def scrape_source(self, source, limit, use_cache=False):
        """Simulate AI-powered web scraping"""
        logger.info(f"🤖 Mock AI Scraping Agent: Analyzing {source} for {limit} startups")
        time.sleep(2)  # Simulate processing time
        
        # Generate mock startup data
        mock_startups = []
        for i in range(limit):
            startup = {
                'name': f'{source.title()}Startup{i+1}',
                'description': f'AI-driven startup in the {source} ecosystem',
                'industry': random.choice(['AI/ML', 'SaaS', 'FinTech', 'HealthTech', 'EdTech']),
                'stage': random.choice(['Seed', 'Series A', 'Series B']),
                'contact_email': f'contact@{source}startup{i+1}.com',
                'website': f'https://{source}startup{i+1}.com',
                'match_score': random.randint(60, 95)
            }
            mock_startups.append(startup)
        
        return mock_startups

class MockSemanticMatchingAgent:
    """Mock AI Agent for Semantic Matching"""
    
    def find_matches_with_ai(self, startups, user_profile, limit=10):
        """Simulate AI-powered semantic matching"""
        logger.info(f"🤖 Mock AI Matching Agent: Analyzing {len(startups)} startups using simulated GPT-4")
        time.sleep(3)  # Simulate AI processing
        
        # Sort by match score and return top matches
        sorted_startups = sorted(startups, key=lambda x: x.get('match_score', 70), reverse=True)
        matches = []
        
        for startup in sorted_startups[:limit]:
            matches.append({
                'startup': startup,
                'score': startup.get('match_score', 70),
                'reasoning': f"Strong alignment with {user_profile.get('skills', ['development'])[0]} skills and {startup.get('industry', 'tech')} industry focus"
            })
        
        return matches

class MockEmailGenerationAgent:
    """Mock AI Agent for Email Generation"""
    
    def generate_email(self, startup, user_profile, match_reasoning):
        """Simulate AI-powered email generation using mock GPT-4"""
        startup_name = startup.get('name') if isinstance(startup, dict) else startup.name
        startup_industry = startup.get('industry') if isinstance(startup, dict) else startup.industry
        startup_stage = startup.get('stage') if isinstance(startup, dict) else startup.stage
        
        logger.info(f"🤖 Mock AI Email Agent: Generating personalized email for {startup_name}")
        time.sleep(1)  # Simulate AI processing
        
        subject = f"Experienced {user_profile.get('skills', ['Developer'])[0]} Developer for {startup_name}"
        
        body = f"""Hi {startup_name} team,

I hope this email finds you well. I came across {startup_name} and was impressed by your work in {startup_industry}.

As an experienced {user_profile.get('experience', 'developer')} with expertise in {', '.join(user_profile.get('skills', ['Python', 'AI']))}, I believe I could contribute significantly to your {startup_stage} stage company.

{match_reasoning}

I'd love to discuss how my background could help {startup_name} achieve its goals. Would you be available for a brief call this week?

Best regards,
{user_profile.get('name', 'AI Developer')}
{user_profile.get('email', 'developer@example.com')}"""
        
        return {
            'subject': subject,
            'body': body
        }

class MockEmailDispatchAgent:
    """Mock AI Agent for Email Dispatch"""
    
    def send_email(self, to_email, subject, body, startup_name):
        """Simulate AI-powered email dispatch"""
        logger.info(f"🤖 Mock AI Dispatch Agent: Sending email to {startup_name}")
        time.sleep(0.5)  # Simulate sending
        
        # Simulate success/failure (90% success rate)
        return random.random() > 0.1

# Initialize AI Agents (Real or Mock)
def initialize_ai_agents():
    """Initialize either real or mock AI agents based on configuration"""
    
    if REAL_AI_AVAILABLE and USE_REAL_AI and OPENAI_API_KEY:
        logger.info("🧠 Initializing REAL AI Agents with GPT-4 + Sentence Transformers")
        real_agents = create_real_ai_agents(OPENAI_API_KEY)
        return {
            'web_scraping': real_agents['web_scraping'],
            'semantic_matching': real_agents['semantic_matching'],
            'email_generation': real_agents['email_generation'],
            'email_dispatch': real_agents['email_dispatch'],
            'type': 'REAL_AI'
        }
    else:
        logger.info("🤖 Initializing Mock AI Agents (simulation mode)")
        return {
            'web_scraping': MockWebScrapingAgent(),
            'semantic_matching': MockSemanticMatchingAgent(),
            'email_generation': MockEmailGenerationAgent(),
            'email_dispatch': MockEmailDispatchAgent(),
            'type': 'MOCK_AI'
        }

# Initialize AI agents
ai_agents = initialize_ai_agents()

# Forms
class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    experience = TextAreaField('Experience Summary', validators=[DataRequired()])
    linkedin = StringField('LinkedIn URL', validators=[OptionalValidator()])
    github = StringField('GitHub URL', validators=[OptionalValidator()])
    submit = SubmitField('Save Profile')

class StartupUploadForm(FlaskForm):
    startup_file = FileField('Startup Database (CSV)', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload Startups')

class MatchingConfigForm(FlaskForm):
    min_score_threshold = FloatField('Minimum Score Threshold', default=0.6)
    email_tone = SelectField('Email Tone', choices=[
        ('confident', 'Confident'),
        ('professional', 'Professional'),
        ('casual', 'Casual')
    ], default='confident')
    email_length = SelectField('Email Length', choices=[
        ('concise', 'Concise'),
        ('detailed', 'Detailed'),
        ('brief', 'Brief')
    ], default='concise')
    auto_send = BooleanField('Auto-send high-scoring matches')
    submit = SubmitField('Update Configuration')

# Routes
@app.route('/')
def index():
    """Main AI Cold Outreach System Interface"""
    return render_template('outreach.html', ai_type=ai_agents['type'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Profile management page."""
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Create user profile from form data
        profile_data = {
            "name": form.name.data,
            "title": form.title.data,
            "email": form.email.data,
            "experience": form.experience.data,
            "linkedin": form.linkedin.data or None,
            "github": form.github.data or None,
            "projects": session.get('projects', []),
            "skills": session.get('skills', [])
        }
        
        # Save to session
        session['user_profile'] = profile_data
        flash('Profile saved successfully!', 'success')
        return redirect(url_for('projects'))
    
    # Load existing profile if available
    if 'user_profile' in session:
        form.name.data = session['user_profile'].get('name', '')
        form.title.data = session['user_profile'].get('title', '')
        form.email.data = session['user_profile'].get('email', '')
        form.experience.data = session['user_profile'].get('experience', '')
        form.linkedin.data = session['user_profile'].get('linkedin', '')
        form.github.data = session['user_profile'].get('github', '')
    
    return render_template('profile.html', form=form)

@app.route('/projects')
def projects():
    """Projects management page."""
    projects = session.get('projects', [])
    return render_template('projects.html', projects=projects)

@app.route('/api/projects', methods=['POST'])
def add_project():
    """Add a new project via API."""
    data = request.get_json()
    
    project = {
        "name": data['name'],
        "description": data['description'],
        "tech_stack": data['tech_stack'].split(','),
        "outcomes": data['outcomes'].split(','),
        "duration": data.get('duration', ''),
        "role": data.get('role', '')
    }
    
    projects = session.get('projects', [])
    projects.append(project)
    session['projects'] = projects
    
    return jsonify({"success": True, "project": project})

@app.route('/api/projects/<int:index>', methods=['DELETE'])
def delete_project(index):
    """Delete a project."""
    projects = session.get('projects', [])
    if 0 <= index < len(projects):
        del projects[index]
        session['projects'] = projects
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid index"})

@app.route('/startups', methods=['GET', 'POST'])
def startups():
    """Startup database management."""
    form = StartupUploadForm()
    
    if form.validate_on_submit():
        file = form.startup_file.data
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        try:
            # Simple CSV reading without pandas
            with open(filepath, 'r') as f:
                lines = f.readlines()
                startups_count = len(lines) - 1  # Subtract header
            session['startups_file'] = str(filepath)
            session['startups_count'] = startups_count
            flash(f'Successfully loaded {startups_count} startups!', 'success')
        except Exception as e:
            flash(f'Error loading startups: {str(e)}', 'error')
        
        return redirect(url_for('startups'))
    
    startups_count = session.get('startups_count', 0)
    startups_file = session.get('startups_file', '')
    
    return render_template('startups.html', form=form, 
                         startups_count=startups_count, 
                         startups_file=startups_file)

@app.route('/match', methods=['GET', 'POST'])
def match():
    """Matching and email generation page."""
    form = MatchingConfigForm()
    
    if form.validate_on_submit():
        # Update configuration
        config = {
            "min_score_threshold": form.min_score_threshold.data,
            "email_tone": form.email_tone.data,
            "email_length": form.email_length.data,
            "auto_send": form.auto_send.data
        }
        session['matching_config'] = config
        flash('Configuration updated!', 'success')
    
    # Load existing config
    if 'matching_config' in session:
        form.min_score_threshold.data = session['matching_config'].get('min_score_threshold', 0.6)
        form.email_tone.data = session['matching_config'].get('email_tone', 'confident')
        form.email_length.data = session['matching_config'].get('email_length', 'concise')
        form.auto_send.data = session['matching_config'].get('auto_send', False)
    
    return render_template('match.html', form=form)

@app.route('/api/match', methods=['POST'])
def run_matching():
    """Run the matching process via API."""
    try:
        # Check if we have all required data
        if 'user_profile' not in session:
            return jsonify({"success": False, "error": "No user profile found"})
        
        if 'startups_file' not in session:
            return jsonify({"success": False, "error": "No startup database loaded"})
        
        # For now, return a demo response
        demo_matches = [
            {
                "company_name": "TechFlow",
                "contact_name": "John Smith",
                "contact_email": "john@techflow.com",
                "match_score": 0.85,
                "tech_stack_alignment": 0.9,
                "domain_alignment": 0.8,
                "project_relevance": 0.85,
                "relevant_projects": ["E-commerce Platform", "API Development"],
                "rationale": "Strong tech stack alignment with React and Node.js experience. Domain expertise in e-commerce platforms.",
                "subject_line": "Experienced Full-Stack Developer for TechFlow",
                "email_body": "Hi John,\n\nI came across TechFlow and was impressed by your AI-powered workflow automation platform...",
                "auto_send": True
            },
            {
                "company_name": "DataViz",
                "contact_name": "Sarah Johnson",
                "contact_email": "sarah@dataviz.com",
                "match_score": 0.75,
                "tech_stack_alignment": 0.8,
                "domain_alignment": 0.7,
                "project_relevance": 0.75,
                "relevant_projects": ["Dashboard Development", "Data Visualization"],
                "rationale": "Good alignment with JavaScript and data visualization technologies.",
                "subject_line": "Full-Stack Developer with Data Visualization Experience",
                "email_body": "Hi Sarah,\n\nI noticed DataViz is building real-time data visualization tools...",
                "auto_send": False
            }
        ]
        
        return jsonify({
            "success": True,
            "matches": demo_matches,
            "total_matches": len(demo_matches),
            "average_score": 0.8,
            "batch_file": "demo_batch.json"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/emails')
def emails():
    """Email management and sending page."""
    # Create demo batch for now
    demo_batch = {
        "total_matches": 2,
        "average_score": 0.8,
        "generated_at": datetime.now().isoformat(),
        "matches": [
            {
                "company_name": "TechFlow",
                "contact_name": "John Smith",
                "contact_email": "john@techflow.com",
                "match_score": 0.85,
                "subject_line": "Experienced Full-Stack Developer for TechFlow",
                "email_body": "Hi John,\n\nI came across TechFlow and was impressed by your AI-powered workflow automation platform. With my experience building scalable e-commerce platforms using React and Node.js, I believe I could contribute significantly to your team.\n\nBest regards,\n[Your Name]",
                "auto_send": True,
                "rationale": {"reasoning": "Strong tech stack alignment with React and Node.js experience."},
                "relevant_projects": ["E-commerce Platform", "API Development"]
            },
            {
                "company_name": "DataViz",
                "contact_name": "Sarah Johnson",
                "contact_email": "sarah@dataviz.com",
                "match_score": 0.75,
                "subject_line": "Full-Stack Developer with Data Visualization Experience",
                "email_body": "Hi Sarah,\n\nI noticed DataViz is building real-time data visualization tools. My background in JavaScript and dashboard development aligns well with your mission.\n\nBest regards,\n[Your Name]",
                "auto_send": False,
                "rationale": {"reasoning": "Good alignment with JavaScript and data visualization technologies."},
                "relevant_projects": ["Dashboard Development", "Data Visualization"]
            }
        ]
    }
    
    return render_template('emails.html', batch=demo_batch)

@app.route('/outreach')
def outreach():
    """Main autonomous outreach interface"""
    return render_template('outreach.html', ai_type=ai_agents['type'])

@app.route('/analytics')
def analytics():
    """Analytics and insights page."""
    analytics_data = {
        "total_matches": 2,
        "average_score": 0.8,
        "score_distribution": {
            "high": 1,
            "medium": 1,
            "low": 0
        },
        "component_scores": {
            "tech_stack": 0.85,
            "domain": 0.75,
            "project": 0.8
        },
        "top_companies": ["TechFlow", "DataViz"]
    }
    
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/settings')
def settings():
    """Settings and configuration page."""
    email_config = {"valid": False, "errors": ["Not configured"]}
    return render_template('settings.html', email_config=email_config)

@app.route('/api/outreach/scrape', methods=['POST'])
def api_scrape_startups():
    """AI Web Scraping Agent Endpoint"""
    try:
        data = request.get_json()
        sources = data.get('sources', ['ycombinator'])
        limit = data.get('limit', 30)
        use_cache = data.get('use_cache', False)
        
        agent_type = ai_agents['type']
        logger.info(f"Deploying {agent_type} Scraping Agent: sources={sources}, limit={limit}")
        
        # Deploy AI scraping agent
        results = []
        total_scraped = 0
        
        for source in sources:
            try:
                scraped_data = ai_agents['web_scraping'].scrape_source(source, limit, use_cache)
                
                # Convert to dict format for session storage
                if scraped_data and hasattr(scraped_data[0], '__dict__'):
                    # Real AI agents return StartupData objects
                    scraped_data = [startup.__dict__ for startup in scraped_data]
                
                results.extend(scraped_data)
                total_scraped += len(scraped_data)
                logger.info(f"{agent_type} Agent scraped {len(scraped_data)} startups from {source}")
            except Exception as e:
                logger.error(f"{agent_type} Agent error scraping {source}: {str(e)}")
                continue
        
        # Store in session for next AI agents
        session['scraped_startups'] = results
        
        return jsonify({
            'success': True,
            'total_scraped': total_scraped,
            'sources_used': sources,
            'ai_type': agent_type,
            'message': f'{agent_type} Agent successfully scraped {total_scraped} startups from {len(sources)} source(s)'
        })
        
    except Exception as e:
        logger.error(f"AI Scraping Agent error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/outreach/match', methods=['POST'])
def api_match_startups():
    """AI Semantic Matching Agent Endpoint"""
    try:
        data = request.get_json()
        method = data.get('method', 'ai_prompt')
        match_count = data.get('match_count', 10)
        
        # Get scraped startups from previous AI agent
        scraped_data = session.get('scraped_startups', [])
        if not scraped_data:
            return jsonify({
                'success': False,
                'error': 'No scraped data found. Please deploy scraping agent first.'
            }), 400
        
        agent_type = ai_agents['type']
        logger.info(f"Deploying {agent_type} Matching Agent: method={method}, count={match_count}")
        
        # Load user profile for AI matching
        profile_path = 'sample_profile.json'
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                user_profile = json.load(f)
        else:
            user_profile = {
                "name": "AI Developer",
                "skills": ["Python", "Machine Learning", "Web Development"],
                "experience": "5+ years in AI and software development",
                "email": "developer@example.com"
            }
        
        # Deploy AI matching agent
        matches = ai_agents['semantic_matching'].find_matches_with_ai(scraped_data, user_profile, limit=match_count)
        
        # Store matches for next AI agent
        session['matched_startups'] = matches
        
        logger.info(f"{agent_type} Matching Agent found {len(matches)} quality matches")
        
        return jsonify({
            'success': True,
            'matches_found': len(matches),
            'method_used': method,
            'ai_type': agent_type,
            'message': f'{agent_type} Agent found {len(matches)} high-quality matches using {method} analysis'
        })
        
    except Exception as e:
        logger.error(f"AI Matching Agent error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/outreach/generate-emails', methods=['POST'])
def api_generate_emails():
    """AI Email Generation Agent Endpoint"""
    try:
        # Get matched startups from previous AI agent
        matched_data = session.get('matched_startups', [])
        if not matched_data:
            return jsonify({
                'success': False,
                'error': 'No matched startups found. Please deploy matching agent first.'
            }), 400
        
        agent_type = ai_agents['type']
        logger.info(f"Deploying {agent_type} Email Generation Agent for {len(matched_data)} matches")
        
        # Load user profile
        profile_path = 'sample_profile.json'
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                user_profile = json.load(f)
        else:
            user_profile = {
                "name": "AI Developer",
                "email": "developer@example.com",
                "skills": ["Python", "Machine Learning", "Web Development"],
                "experience": "5+ years in AI and software development"
            }
        
        # Deploy AI email generation agent
        generated_emails = []
        for match_data in matched_data:
            startup = match_data['startup']
            
            try:
                email_content = ai_agents['email_generation'].generate_email(
                    startup=startup,
                    user_profile=user_profile,
                    match_reasoning=match_data.get('reasoning', '')
                )
                
                startup_name = startup.get('name') if isinstance(startup, dict) else startup.name
                startup_email = startup.get('contact_email') if isinstance(startup, dict) else startup.contact_email
                
                generated_emails.append({
                    'startup_name': startup_name,
                    'recipient_email': startup_email,
                    'subject': email_content['subject'],
                    'body': email_content['body'],
                    'match_score': match_data['score']
                })
                
            except Exception as e:
                startup_name = startup.get('name') if isinstance(startup, dict) else startup.name
                logger.error(f"AI Email Agent error for {startup_name}: {str(e)}")
                continue
        
        # Store generated emails for dispatch agent
        session['generated_emails'] = generated_emails
        
        logger.info(f"{agent_type} Email Generation Agent created {len(generated_emails)} personalized emails")
        
        model_info = "GPT-4" if agent_type == "REAL_AI" else "simulated GPT-4"
        
        return jsonify({
            'success': True,
            'emails_generated': len(generated_emails),
            'emails': generated_emails[:3],  # Return first 3 for preview
            'ai_type': agent_type,
            'message': f'{agent_type} Agent generated {len(generated_emails)} personalized emails using {model_info}'
        })
        
    except Exception as e:
        logger.error(f"AI Email Generation Agent error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/outreach/send-emails', methods=['POST'])
def api_send_emails():
    """AI Email Dispatch Agent Endpoint"""
    try:
        # Get generated emails from previous AI agent
        emails = session.get('generated_emails', [])
        if not emails:
            return jsonify({
                'success': False,
                'error': 'No generated emails found. Please deploy email generation agent first.'
            }), 400
        
        agent_type = ai_agents['type']
        logger.info(f"Deploying {agent_type} Email Dispatch Agent for {len(emails)} emails")
        
        # Deploy AI email dispatch agent
        sent_count = 0
        failed_count = 0
        
        for email in emails:
            try:
                success = ai_agents['email_dispatch'].send_email(
                    to_email=email['recipient_email'],
                    subject=email['subject'],
                    body=email['body'],
                    startup_name=email['startup_name']
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"AI Dispatch Agent error for {email['startup_name']}: {str(e)}")
                failed_count += 1
        
        # Generate AI-powered campaign report
        report_data = {
            'campaign_date': datetime.now().isoformat(),
            'total_emails': len(emails),
            'sent_successfully': sent_count,
            'failed': failed_count,
            'success_rate': (sent_count / len(emails)) * 100 if emails else 0,
            'ai_type': agent_type,
            'ai_agents_used': ['Web Scraping', 'Semantic Matching', 'Email Generation', 'Email Dispatch'],
            'emails_sent': emails
        }
        
        # Save AI campaign report
        report_filename = f"ai_campaign_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('uploads', exist_ok=True)
        with open(f"uploads/{report_filename}", 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"{agent_type} Campaign completed: {sent_count} sent, {failed_count} failed")
        
        return jsonify({
            'success': True,
            'emails_sent': sent_count,
            'emails_failed': failed_count,
            'success_rate': report_data['success_rate'],
            'report_file': report_filename,
            'ai_type': agent_type,
            'message': f'{agent_type} Agent campaign completed: {sent_count} emails sent successfully'
        })
        
    except Exception as e:
        logger.error(f"AI Email Dispatch Agent error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    agent_type = ai_agents['type']
    print("🤖 Starting AI-Powered Cold Outreach System...")
    print(f"🧠 AI Mode: {agent_type}")
    
    if agent_type == 'REAL_AI':
        print("🧠 Real AI Agents: GPT-4 | Sentence Transformers | OpenAI Embeddings")
    else:
        print("🤖 Mock AI Agents: Simulated GPT-4 | Mock Embeddings | Demo Mode")
        print("💡 To enable real AI: Set OPENAI_API_KEY and USE_REAL_AI=true")
    
    print("📱 Open your browser and go to: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("--------------------------------------------------")
    
    # Ensure uploads directory exists
    os.makedirs('uploads', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True) 