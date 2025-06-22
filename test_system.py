#!/usr/bin/env python3
"""
Test script for Cold Outreach AI Matchmaker

This script demonstrates the full functionality of the system
without requiring external API keys or email configuration.
"""

import json
import os
from datetime import datetime

from data_models import MatchingConfig, EmailBatch
from matcher import SemanticMatcher
from email_generator import EmailGenerator
from utils import create_sample_profile, create_sample_startups, format_match_summary


def test_matching_system():
    """Test the complete matching and email generation system."""
    
    print("🚀 Testing Cold Outreach AI Matchmaker System")
    print("=" * 60)
    
    # Create sample data
    print("\n📄 Creating sample user profile...")
    user_profile = create_sample_profile()
    print(f"✅ Created profile for {user_profile.name}")
    print(f"   - {len(user_profile.projects)} projects")
    print(f"   - {len(user_profile.skills)} skills")
    
    print("\n🏢 Creating sample startups...")
    startups = create_sample_startups()
    print(f"✅ Created {len(startups)} sample startups")
    
    # Configure matching
    print("\n⚙️ Configuring matching system...")
    config = MatchingConfig(
        min_score_threshold=0.5,
        email_tone="confident",
        email_length="concise"
    )
    
    # Initialize matcher
    print("🤖 Initializing semantic matcher...")
    matcher = SemanticMatcher(config)
    
    # Find matches
    print("\n🔍 Finding matches...")
    matches = matcher.find_matches(user_profile, startups)
    
    if not matches:
        print("❌ No matches found!")
        return
    
    print(f"✅ Found {len(matches)} matches")
    
    # Show match summary
    print("\n" + "=" * 60)
    print("MATCH SUMMARY")
    print("=" * 60)
    print(format_match_summary(matches))
    
    # Generate emails
    print("\n✍️ Generating personalized emails...")
    email_generator = EmailGenerator(config=config)
    
    # We need to create startup objects for email generation
    # For this test, we'll use the sample startups directly
    matches_with_emails = []
    
    for match in matches:
        # Find the corresponding startup
        startup = next((s for s in startups if s.company_name == match.company_name), None)
        
        if startup:
            # Generate email content
            email_content = email_generator.generate_email(
                user_profile=user_profile,
                startup=startup,
                match_rationale=match.rationale.dict(),
                relevant_projects=match.relevant_projects
            )
            
            # Update match with email content
            match.email_body = email_content["email_body"]
            match.subject_line = email_content["subject_line"]
            
            matches_with_emails.append(match)
    
    print(f"✅ Generated {len(matches_with_emails)} emails")
    
    # Create email batch
    batch = EmailBatch(
        user_profile=user_profile,
        matches=matches_with_emails,
        total_matches=len(matches_with_emails),
        average_score=sum(m.match_score for m in matches_with_emails) / len(matches_with_emails),
        generated_at=datetime.now().isoformat()
    )
    
    # Save results
    print("\n💾 Saving results...")
    with open('test_results.json', 'w') as f:
        json.dump(batch.dict(), f, indent=2, default=str)
    print("✅ Saved results to test_results.json")
    
    # Show sample emails
    print("\n" + "=" * 60)
    print("SAMPLE EMAILS")
    print("=" * 60)
    
    for i, match in enumerate(matches_with_emails[:3], 1):
        print(f"\n{i}. {match.company_name} (Score: {match.match_score:.2f})")
        print(f"   To: {match.contact_name or 'Team'} <{match.contact_email or 'N/A'}>")
        print(f"   Subject: {match.subject_line}")
        print("-" * 40)
        print(match.email_body)
        print("=" * 60)
    
    # Show statistics
    print("\n📊 SYSTEM STATISTICS")
    print("=" * 60)
    
    scores = [m.match_score for m in matches_with_emails]
    tech_scores = [m.rationale.tech_stack_alignment for m in matches_with_emails]
    domain_scores = [m.rationale.domain_alignment for m in matches_with_emails]
    project_scores = [m.rationale.project_relevance for m in matches_with_emails]
    
    print(f"Total matches: {len(matches_with_emails)}")
    print(f"Average match score: {sum(scores) / len(scores):.3f}")
    print(f"Average tech stack alignment: {sum(tech_scores) / len(tech_scores):.3f}")
    print(f"Average domain alignment: {sum(domain_scores) / len(domain_scores):.3f}")
    print(f"Average project relevance: {sum(project_scores) / len(project_scores):.3f}")
    
    # Score distribution
    high_matches = len([s for s in scores if s >= 0.8])
    medium_matches = len([s for s in scores if 0.6 <= s < 0.8])
    low_matches = len([s for s in scores if s < 0.6])
    
    print(f"\nScore distribution:")
    print(f"  High (≥0.8): {high_matches}")
    print(f"  Medium (0.6-0.8): {medium_matches}")
    print(f"  Low (<0.6): {low_matches}")
    
    print("\n🎉 Test completed successfully!")
    print("\nNext steps:")
    print("1. Review test_results.json for detailed results")
    print("2. Customize sample_profile.json with your information")
    print("3. Add your startup database to sample_startups.csv")
    print("4. Set up your .env file with API keys and email settings")
    print("5. Run: python main.py match --profile sample_profile.json --startups sample_startups.csv")


def test_individual_components():
    """Test individual components of the system."""
    
    print("\n🧪 Testing Individual Components")
    print("=" * 60)
    
    # Test data models
    print("\n📋 Testing data models...")
    try:
        user_profile = create_sample_profile()
        startups = create_sample_startups()
        print("✅ Data models working correctly")
    except Exception as e:
        print(f"❌ Data models error: {e}")
        return
    
    # Test matcher
    print("\n🤖 Testing semantic matcher...")
    try:
        config = MatchingConfig()
        matcher = SemanticMatcher(config)
        matches = matcher.find_matches(user_profile, startups)
        print(f"✅ Matcher working: found {len(matches)} matches")
    except Exception as e:
        print(f"❌ Matcher error: {e}")
        return
    
    # Test email generator
    print("\n✍️ Testing email generator...")
    try:
        email_generator = EmailGenerator()
        if matches:
            match = matches[0]
            startup = next((s for s in startups if s.company_name == match.company_name), None)
            if startup:
                email_content = email_generator.generate_email(
                    user_profile, startup, match.rationale.dict(), match.relevant_projects
                )
                print("✅ Email generator working")
                print(f"   Subject: {email_content['subject_line']}")
                print(f"   Body length: {len(email_content['email_body'])} characters")
    except Exception as e:
        print(f"❌ Email generator error: {e}")
        return
    
    print("\n✅ All components tested successfully!")


if __name__ == "__main__":
    # Test individual components first
    test_individual_components()
    
    # Test full system
    test_matching_system() 