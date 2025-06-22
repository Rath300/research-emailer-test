#!/usr/bin/env python3
"""
Cold Outreach AI Matchmaker - CLI Interface

A comprehensive system for automating cold email outreach to early-stage startups
by matching your past projects and experiences with relevant companies.
"""

import click
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from data_models import MatchingConfig, EmailConfig
from matcher import SemanticMatcher
from email_generator import EmailGenerator
from email_dispatcher import EmailDispatcher
from utils import (
    load_user_profile, load_startups, save_email_batch, load_email_batch,
    export_matches_to_csv, create_sample_profile, create_sample_startups,
    validate_email_config, format_match_summary, create_env_template
)

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Cold Outreach AI Matchmaker - Automate your startup outreach with AI-powered matching."""
    pass


@cli.command()
@click.option('--profile', '-p', required=True, help='Path to user profile (JSON or Markdown)')
@click.option('--startups', '-s', required=True, help='Path to startups CSV file')
@click.option('--output', '-o', default='matches.json', help='Output file for matches')
@click.option('--min-score', default=0.6, help='Minimum match score threshold')
@click.option('--auto-send', is_flag=True, help='Automatically send emails for high-scoring matches')
@click.option('--preview', is_flag=True, help='Preview matches before processing')
@click.option('--export-csv', help='Export matches to CSV file')
def match(profile, startups, output, min_score, auto_send, preview, export_csv):
    """Find matches between your profile and startups, generate emails."""
    
    click.echo("🔍 Starting cold outreach matching process...")
    
    try:
        # Load user profile
        click.echo(f"📄 Loading user profile from {profile}...")
        user_profile = load_user_profile(profile)
        click.echo(f"✅ Loaded profile for {user_profile.name}")
        
        # Load startups
        click.echo(f"🏢 Loading startups from {startups}...")
        startup_list = load_startups(startups)
        click.echo(f"✅ Loaded {len(startup_list)} startups")
        
        # Configure matching
        config = MatchingConfig(min_score_threshold=min_score)
        matcher = SemanticMatcher(config)
        
        # Find matches
        click.echo("🤖 Finding matches using semantic analysis...")
        matches = matcher.find_matches(user_profile, startup_list)
        
        if not matches:
            click.echo("❌ No matches found above the threshold score.")
            return
        
        click.echo(f"✅ Found {len(matches)} matches")
        
        # Generate emails
        click.echo("✍️ Generating personalized emails...")
        email_generator = EmailGenerator(config=config)
        matches_with_emails = email_generator.generate_emails_for_matches(user_profile, matches)
        
        # Set auto-send flag for high-scoring matches
        if auto_send:
            for match in matches_with_emails:
                if match.match_score >= 0.8:
                    match.auto_send = True
        
        # Preview matches if requested
        if preview:
            click.echo("\n" + "="*60)
            click.echo("MATCH PREVIEW")
            click.echo("="*60)
            click.echo(format_match_summary(matches_with_emails))
            
            if not click.confirm("\nContinue with email generation?"):
                click.echo("❌ Process cancelled.")
                return
        
        # Create email batch
        from data_models import EmailBatch
        batch = EmailBatch(
            user_profile=user_profile,
            matches=matches_with_emails,
            total_matches=len(matches_with_emails),
            average_score=sum(m.match_score for m in matches_with_emails) / len(matches_with_emails),
            generated_at=datetime.now().isoformat()
        )
        
        # Save results
        save_email_batch(batch, output)
        click.echo(f"💾 Saved matches to {output}")
        
        # Export to CSV if requested
        if export_csv:
            csv_path = export_matches_to_csv(matches_with_emails, export_csv)
            click.echo(f"📊 Exported to CSV: {csv_path}")
        
        # Send emails if auto-send is enabled
        if auto_send:
            click.echo("📧 Sending emails...")
            dispatcher = EmailDispatcher()
            
            # Validate email configuration
            config_validation = dispatcher.validate_config()
            if not config_validation["valid"]:
                click.echo("❌ Email configuration invalid:")
                for error in config_validation["errors"]:
                    click.echo(f"   - {error}")
                click.echo("\nPlease set up your email configuration in .env file")
                return
            
            # Send emails
            results = dispatcher.send_batch_emails(matches_with_emails, user_profile, auto_send=True)
            
            click.echo(f"📤 Email sending complete:")
            click.echo(f"   ✅ Sent: {results['sent']}")
            click.echo(f"   ❌ Failed: {results['failed']}")
            click.echo(f"   ⏭️ Skipped: {results['skipped']}")
        
        # Show summary
        click.echo("\n" + "="*60)
        click.echo("MATCHING COMPLETE")
        click.echo("="*60)
        click.echo(format_match_summary(matches_with_emails))
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        raise


@cli.command()
@click.option('--profile', '-p', required=True, help='Path to user profile (JSON or Markdown)')
@click.option('--startups', '-s', required=True, help='Path to startups CSV file')
@click.option('--output', '-o', default='emails.json', help='Output file for generated emails')
@click.option('--min-score', default=0.6, help='Minimum match score threshold')
def generate(profile, startups, output, min_score):
    """Generate emails only (no sending)."""
    
    click.echo("✍️ Generating emails...")
    
    try:
        # Load data
        user_profile = load_user_profile(profile)
        startup_list = load_startups(startups)
        
        # Configure and match
        config = MatchingConfig(min_score_threshold=min_score)
        matcher = SemanticMatcher(config)
        matches = matcher.find_matches(user_profile, startup_list)
        
        if not matches:
            click.echo("❌ No matches found.")
            return
        
        # Generate emails
        email_generator = EmailGenerator(config=config)
        matches_with_emails = email_generator.generate_emails_for_matches(user_profile, matches)
        
        # Save results
        from data_models import EmailBatch
        batch = EmailBatch(
            user_profile=user_profile,
            matches=matches_with_emails,
            total_matches=len(matches_with_emails),
            average_score=sum(m.match_score for m in matches_with_emails) / len(matches_with_emails),
            generated_at=datetime.now().isoformat()
        )
        
        save_email_batch(batch, output)
        click.echo(f"✅ Generated {len(matches_with_emails)} emails, saved to {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        raise


@cli.command()
@click.option('--emails', '-e', required=True, help='Path to email batch JSON file')
@click.option('--auto-send', is_flag=True, help='Automatically send emails')
@click.option('--preview', is_flag=True, help='Preview emails before sending')
def send(emails, auto_send, preview):
    """Send emails from a generated batch."""
    
    click.echo("📧 Email sending process...")
    
    try:
        # Load email batch
        batch = load_email_batch(emails)
        click.echo(f"📄 Loaded {batch.total_matches} emails from {emails}")
        
        # Validate email configuration
        dispatcher = EmailDispatcher()
        config_validation = dispatcher.validate_config()
        
        if not config_validation["valid"]:
            click.echo("❌ Email configuration invalid:")
            for error in config_validation["errors"]:
                click.echo(f"   - {error}")
            click.echo("\nPlease set up your email configuration in .env file")
            return
        
        # Preview if requested
        if preview:
            click.echo("\n" + "="*60)
            click.echo("EMAIL PREVIEW")
            click.echo("="*60)
            
            for i, match in enumerate(batch.matches[:3], 1):  # Show first 3
                click.echo(f"\n{i}. To: {match.contact_name or 'Team'} <{match.contact_email or 'N/A'}>")
                click.echo(f"   Subject: {match.subject_line}")
                click.echo(f"   Score: {match.match_score:.2f}")
                click.echo(f"   Auto-send: {match.auto_send}")
                click.echo("-" * 40)
                click.echo(match.email_body[:200] + "..." if len(match.email_body) > 200 else match.email_body)
            
            if not click.confirm(f"\nSend {len(batch.matches)} emails?"):
                click.echo("❌ Sending cancelled.")
                return
        
        # Send emails
        results = dispatcher.send_batch_emails(batch.matches, batch.user_profile, auto_send=auto_send)
        
        # Show results
        click.echo(f"\n📤 Email sending complete:")
        click.echo(f"   ✅ Sent: {results['sent']}")
        click.echo(f"   ❌ Failed: {results['failed']}")
        click.echo(f"   ⏭️ Skipped: {results['skipped']}")
        
        # Export results
        results_file = dispatcher.export_results()
        click.echo(f"📊 Results saved to: {results_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        raise


@cli.command()
@click.option('--profile', '-p', help='Path to user profile file')
@click.option('--startups', '-s', help='Path to startups CSV file')
def validate(profile, startups):
    """Validate configuration and data files."""
    
    click.echo("🔍 Validating configuration...")
    
    # Validate email configuration
    email_config = validate_email_config()
    if email_config["valid"]:
        click.echo("✅ Email configuration is valid")
    else:
        click.echo("❌ Email configuration issues:")
        for var in email_config["missing_vars"]:
            click.echo(f"   - Missing: {var}")
    
    # Validate profile if provided
    if profile:
        try:
            user_profile = load_user_profile(profile)
            click.echo(f"✅ Profile valid: {user_profile.name} ({len(user_profile.projects)} projects)")
        except Exception as e:
            click.echo(f"❌ Profile validation failed: {str(e)}")
    
    # Validate startups if provided
    if startups:
        try:
            startup_list = load_startups(startups)
            click.echo(f"✅ Startups valid: {len(startup_list)} companies loaded")
        except Exception as e:
            click.echo(f"❌ Startups validation failed: {str(e)}")
    
    # Check OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        click.echo("✅ OpenAI API key configured")
    else:
        click.echo("⚠️ OpenAI API key not configured (will use template emails)")


@cli.command()
def init():
    """Initialize the project with sample data and configuration."""
    
    click.echo("🚀 Initializing Cold Outreach AI Matchmaker...")
    
    # Create .env template
    env_content = create_env_template()
    with open('.env.example', 'w') as f:
        f.write(env_content)
    click.echo("✅ Created .env.example template")
    
    # Create sample profile
    sample_profile = create_sample_profile()
    with open('sample_profile.json', 'w') as f:
        json.dump(sample_profile.dict(), f, indent=2)
    click.echo("✅ Created sample_profile.json")
    
    # Create sample startups
    sample_startups = create_sample_startups()
    import pandas as pd
    startups_data = []
    for startup in sample_startups:
        startups_data.append({
            'company_name': startup.company_name,
            'mission': startup.mission,
            'product': startup.product,
            'tech_stack': ','.join(startup.tech_stack),
            'team_size': startup.team_size,
            'funding_stage': startup.funding_stage.value if startup.funding_stage else '',
            'website': startup.website,
            'contact_email': startup.contact_email,
            'contact_name': startup.contact_name,
            'location': startup.location,
            'industry': startup.industry,
            'description': startup.description
        })
    
    df = pd.DataFrame(startups_data)
    df.to_csv('sample_startups.csv', index=False)
    click.echo("✅ Created sample_startups.csv")
    
    click.echo("\n🎉 Initialization complete!")
    click.echo("\nNext steps:")
    click.echo("1. Copy .env.example to .env and configure your settings")
    click.echo("2. Customize sample_profile.json with your information")
    click.echo("3. Add your startup database to sample_startups.csv")
    click.echo("4. Run: python main.py match --profile sample_profile.json --startups sample_startups.csv")


@cli.command()
@click.option('--emails', '-e', required=True, help='Path to email batch JSON file')
@click.option('--output', '-o', default='matches.csv', help='Output CSV file')
def export(emails, output):
    """Export email matches to CSV for review."""
    
    try:
        batch = load_email_batch(emails)
        csv_path = export_matches_to_csv(batch.matches, output)
        click.echo(f"✅ Exported {len(batch.matches)} matches to {csv_path}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        raise


if __name__ == '__main__':
    cli() 