#!/usr/bin/env python3
"""
Cold Outreach AI Matchmaker - Web Dashboard

A modern web interface for the cold outreach system with interactive features,
real-time matching, and email management.
"""

import os
import json
import tempfile
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

# Suppress TensorFlow warnings that can cause hanging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
warnings.filterwarnings('ignore', category=FutureWarning, module='tensorflow')

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Optional as OptionalValidator
from werkzeug.utils import secure_filename

# Import our modules with error handling
try:
    from data_models import UserProfile, Startup, EmailMatch, MatchingConfig, EmailBatch
    from matcher import SemanticMatcher
    from email_generator import EmailGenerator
    from email_dispatcher import EmailDispatcher
    from utils import (
        load_user_profile, load_startups, save_email_batch, load_email_batch,
        export_matches_to_csv, create_sample_profile, create_sample_startups,
        validate_email_config, format_match_summary
    )
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")
    print("The dashboard will run with limited functionality.")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for session management
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)

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
    """Main dashboard page."""
    return render_template('index.html')

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
            "projects": [],  # Will be added separately
            "skills": []     # Will be added separately
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
            startups = load_startups(str(filepath))
            session['startups_file'] = str(filepath)
            session['startups_count'] = len(startups)
            flash(f'Successfully loaded {len(startups)} startups!', 'success')
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
        
        # Load data
        profile_data = session['user_profile'].copy()
        profile_data['projects'] = session.get('projects', [])
        profile_data['skills'] = session.get('skills', [])
        
        user_profile = UserProfile(**profile_data)
        startups = load_startups(session['startups_file'])
        
        # Configure matching
        config_data = session.get('matching_config', {})
        config = MatchingConfig(
            min_score_threshold=config_data.get('min_score_threshold', 0.6),
            email_tone=config_data.get('email_tone', 'confident'),
            email_length=config_data.get('email_length', 'concise')
        )
        
        # Run matching
        matcher = SemanticMatcher(config)
        matches = matcher.find_matches(user_profile, startups)
        
        if not matches:
            return jsonify({"success": False, "error": "No matches found above threshold"})
        
        # Generate emails
        email_generator = EmailGenerator(config=config)
        matches_with_emails = email_generator.generate_emails_for_matches(user_profile, matches)
        
        # Set auto-send flag
        auto_send = config_data.get('auto_send', False)
        for match in matches_with_emails:
            if auto_send and match.match_score >= 0.8:
                match.auto_send = True
        
        # Create batch
        batch = EmailBatch(
            user_profile=user_profile,
            matches=matches_with_emails,
            total_matches=len(matches_with_emails),
            average_score=sum(m.match_score for m in matches_with_emails) / len(matches_with_emails),
            generated_at=datetime.now().isoformat()
        )
        
        # Save batch
        batch_file = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_email_batch(batch, batch_file)
        session['current_batch'] = batch_file
        
        # Prepare response data
        matches_data = []
        for match in matches_with_emails:
            matches_data.append({
                "company_name": match.company_name,
                "contact_name": match.contact_name,
                "contact_email": match.contact_email,
                "match_score": match.match_score,
                "tech_stack_alignment": match.rationale.tech_stack_alignment,
                "domain_alignment": match.rationale.domain_alignment,
                "project_relevance": match.rationale.project_relevance,
                "relevant_projects": match.relevant_projects,
                "rationale": match.rationale.reasoning,
                "subject_line": match.subject_line,
                "email_body": match.email_body,
                "auto_send": match.auto_send
            })
        
        return jsonify({
            "success": True,
            "matches": matches_data,
            "total_matches": len(matches_with_emails),
            "average_score": batch.average_score,
            "batch_file": batch_file
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/emails')
def emails():
    """Email management and sending page."""
    batch_file = session.get('current_batch')
    if not batch_file or not Path(batch_file).exists():
        flash('No email batch found. Please run matching first.', 'warning')
        return redirect(url_for('match'))
    
    try:
        batch = load_email_batch(batch_file)
        return render_template('emails.html', batch=batch)
    except Exception as e:
        flash(f'Error loading email batch: {str(e)}', 'error')
        return redirect(url_for('match'))

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Send emails via API."""
    try:
        batch_file = session.get('current_batch')
        if not batch_file:
            return jsonify({"success": False, "error": "No email batch found"})
        
        batch = load_email_batch(batch_file)
        
        # Validate email configuration
        dispatcher = EmailDispatcher()
        config_validation = dispatcher.validate_config()
        if not config_validation["valid"]:
            return jsonify({
                "success": False, 
                "error": "Email configuration invalid",
                "details": config_validation["errors"]
            })
        
        # Send emails
        results = dispatcher.send_batch_emails(batch.matches, batch.user_profile, auto_send=True)
        
        # Save results
        results_file = dispatcher.export_results()
        
        return jsonify({
            "success": True,
            "results": results,
            "results_file": results_file
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/analytics')
def analytics():
    """Analytics and insights page."""
    batch_file = session.get('current_batch')
    if not batch_file or not Path(batch_file).exists():
        flash('No data available for analytics. Please run matching first.', 'warning')
        return redirect(url_for('match'))
    
    try:
        batch = load_email_batch(batch_file)
        
        # Prepare analytics data
        scores = [m.match_score for m in batch.matches]
        tech_scores = [m.rationale.tech_stack_alignment for m in batch.matches]
        domain_scores = [m.rationale.domain_alignment for m in batch.matches]
        project_scores = [m.rationale.project_relevance for m in batch.matches]
        
        analytics_data = {
            "total_matches": len(batch.matches),
            "average_score": sum(scores) / len(scores),
            "score_distribution": {
                "high": len([s for s in scores if s >= 0.8]),
                "medium": len([s for s in scores if 0.6 <= s < 0.8]),
                "low": len([s for s in scores if s < 0.6])
            },
            "component_scores": {
                "tech_stack": sum(tech_scores) / len(tech_scores),
                "domain": sum(domain_scores) / len(domain_scores),
                "project": sum(project_scores) / len(project_scores)
            },
            "top_companies": [m.company_name for m in batch.matches[:5]]
        }
        
        return render_template('analytics.html', analytics=analytics_data, batch=batch)
        
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('match'))

@app.route('/api/export/<format>')
def export_data(format):
    """Export data in various formats."""
    batch_file = session.get('current_batch')
    if not batch_file:
        return jsonify({"success": False, "error": "No data to export"})
    
    try:
        batch = load_email_batch(batch_file)
        
        if format == 'csv':
            filename = f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_matches_to_csv(batch.matches, filename)
            return jsonify({"success": True, "filename": filename})
        elif format == 'json':
            return jsonify({"success": True, "data": batch.dict()})
        else:
            return jsonify({"success": False, "error": "Unsupported format"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/settings')
def settings():
    """Settings and configuration page."""
    email_config = validate_email_config()
    return render_template('settings.html', email_config=email_config)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 