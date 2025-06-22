import openai
import os
from typing import List, Dict, Optional
from data_models import UserProfile, Startup, EmailMatch, MatchingConfig
import json
from datetime import datetime


class EmailGenerator:
    def __init__(self, api_key: str = None, config: MatchingConfig = None):
        self.config = config or MatchingConfig()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def _create_email_prompt(self, user_profile: UserProfile, startup: Startup, 
                           match_rationale: Dict, relevant_projects: List[str]) -> str:
        """Create a detailed prompt for email generation."""
        
        # Extract relevant project details
        project_details = []
        for project in user_profile.projects:
            if project.name in relevant_projects:
                project_details.append({
                    "name": project.name,
                    "description": project.description,
                    "tech_stack": project.tech_stack,
                    "outcomes": project.outcomes,
                    "role": project.role
                })
        
        prompt = f"""
You are a professional cold email writer. Create a confident, concise cold email for a startup outreach.

CONTEXT:
- Your name: {user_profile.name}
- Your title: {user_profile.title}
- Your experience: {user_profile.experience}
- Your email: {user_profile.email}

STARTUP INFORMATION:
- Company: {startup.company_name}
- Mission: {startup.mission}
- Product: {startup.product}
- Tech Stack: {', '.join(startup.tech_stack)}
- Funding Stage: {startup.funding_stage or 'Not specified'}
- Team Size: {startup.team_size or 'Not specified'}
- Contact: {startup.contact_name or 'Team'}

MATCH RATIONALE:
- Tech Stack Alignment: {match_rationale.get('tech_stack_alignment', 0):.2f}
- Domain Alignment: {match_rationale.get('domain_alignment', 0):.2f}
- Project Relevance: {match_rationale.get('project_relevance', 0):.2f}
- Overall Score: {match_rationale.get('overall_score', 0):.2f}

RELEVANT PROJECTS:
{json.dumps(project_details, indent=2)}

REQUIREMENTS:
1. Tone: {self.config.email_tone} and professional
2. Length: {self.config.email_length} (aim for 100-150 words)
3. Avoid buzzwords and fluff
4. Be specific about how your experience relates to their needs
5. Include a clear call-to-action
6. Use the contact name if available, otherwise use "Team"
7. Make it personal and relevant to their specific situation

EMAIL STRUCTURE:
- Personalized greeting
- Brief introduction with relevant context
- Specific value proposition based on your projects
- Clear call-to-action
- Professional closing

Generate only the email body (no subject line). Make it ready for mail merge with [Name] placeholder.
"""

        return prompt
    
    def _create_subject_prompt(self, user_profile: UserProfile, startup: Startup, 
                             relevant_projects: List[str]) -> str:
        """Create a prompt for subject line generation."""
        
        prompt = f"""
Generate a compelling email subject line for a cold outreach email.

CONTEXT:
- Your name: {user_profile.name}
- Your title: {user_profile.title}
- Company: {startup.company_name}
- Product: {startup.product}
- Relevant projects: {', '.join(relevant_projects[:2])}

REQUIREMENTS:
1. Keep it under 60 characters
2. Be specific and relevant
3. Avoid spammy words
4. Make it personal and intriguing
5. Focus on value proposition

Generate only the subject line, nothing else.
"""

        return prompt
    
    def generate_email(self, user_profile: UserProfile, startup: Startup, 
                      match_rationale: Dict, relevant_projects: List[str]) -> Dict[str, str]:
        """Generate email body and subject line using OpenAI."""
        
        if not self.api_key:
            # Fallback to template-based generation
            return self._generate_template_email(user_profile, startup, match_rationale, relevant_projects)
        
        try:
            # Generate email body
            email_prompt = self._create_email_prompt(user_profile, startup, match_rationale, relevant_projects)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert cold email writer who creates compelling, personalized outreach emails."},
                    {"role": "user", "content": email_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            email_body = response.choices[0].message.content.strip()
            
            # Generate subject line
            subject_prompt = self._create_subject_prompt(user_profile, startup, relevant_projects)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating compelling email subject lines."},
                    {"role": "user", "content": subject_prompt}
                ],
                max_tokens=20,
                temperature=0.8
            )
            
            subject_line = response.choices[0].message.content.strip()
            
            return {
                "email_body": email_body,
                "subject_line": subject_line
            }
            
        except Exception as e:
            print(f"Error generating email with OpenAI: {e}")
            # Fallback to template-based generation
            return self._generate_template_email(user_profile, startup, match_rationale, relevant_projects)
    
    def _generate_template_email(self, user_profile: UserProfile, startup: Startup, 
                               match_rationale: Dict, relevant_projects: List[str]) -> Dict[str, str]:
        """Generate email using templates when OpenAI is not available."""
        
        # Extract key information
        tech_score = match_rationale.get('tech_stack_alignment', 0)
        domain_score = match_rationale.get('domain_alignment', 0)
        overall_score = match_rationale.get('overall_score', 0)
        
        # Choose template based on scores
        if overall_score > 0.8:
            template = self._get_high_match_template()
        elif overall_score > 0.6:
            template = self._get_medium_match_template()
        else:
            template = self._get_low_match_template()
        
        # Fill template
        contact_name = startup.contact_name or "Team"
        project_names = ", ".join(relevant_projects[:2])
        
        email_body = template.format(
            contact_name=contact_name,
            user_name=user_profile.name,
            user_title=user_profile.title,
            company_name=startup.company_name,
            product=startup.product,
            project_names=project_names,
            experience=user_profile.experience,
            user_email=user_profile.email
        )
        
        # Generate subject line
        if tech_score > 0.6:
            subject = f"Technical expertise for {startup.company_name}"
        elif domain_score > 0.6:
            subject = f"Domain experience for {startup.company_name}"
        else:
            subject = f"Partnership opportunity with {startup.company_name}"
        
        return {
            "email_body": email_body,
            "subject_line": subject
        }
    
    def _get_high_match_template(self) -> str:
        """Template for high-scoring matches."""
        return """Hi {contact_name},

I'm {user_name}, a {user_title} with {experience}. I came across {company_name} and was impressed by your work on {product}.

I believe my experience aligns well with your needs:
• {project_names} - directly relevant to your technical challenges
• Strong background in the technologies you're using
• Experience scaling products in similar domains

I'd love to discuss how I could contribute to {company_name}'s growth. Would you be open to a 15-minute call to explore potential collaboration?

Best regards,
{user_name}
{user_email}"""
    
    def _get_medium_match_template(self) -> str:
        """Template for medium-scoring matches."""
        return """Hi {contact_name},

I'm {user_name}, a {user_title} with {experience}. I've been following {company_name}'s progress with {product} and find your approach interesting.

My background includes {project_names}, which has given me relevant experience in similar problem spaces. I'm particularly drawn to how you're tackling [specific aspect of their product].

I'd appreciate the opportunity to learn more about your technical challenges and discuss potential ways I could add value to your team.

Would you be available for a brief conversation?

Best regards,
{user_name}
{user_email}"""
    
    def _get_low_match_template(self) -> str:
        """Template for lower-scoring matches."""
        return """Hi {contact_name},

I'm {user_name}, a {user_title} with {experience}. I recently discovered {company_name} and was intrigued by your mission with {product}.

While my background in {project_names} may not be a perfect fit, I'm passionate about [relevant domain/technology] and believe I could bring valuable perspective to your team.

I'd love to learn more about your current challenges and explore if there might be a mutually beneficial opportunity to collaborate.

Would you be open to a brief conversation?

Best regards,
{user_name}
{user_email}"""
    
    def generate_emails_for_matches(self, user_profile: UserProfile, 
                                  matches: List[EmailMatch]) -> List[EmailMatch]:
        """Generate emails for all matches."""
        
        for match in matches:
            # Get startup info (this would need to be passed or retrieved)
            # For now, we'll use the rationale data
            startup_info = {
                "company_name": match.company_name,
                "mission": "Building innovative solutions",  # Placeholder
                "product": "Technology platform",  # Placeholder
                "tech_stack": [],  # Would need to be passed
                "funding_stage": None,
                "team_size": None,
                "contact_name": match.contact_name
            }
            
            # Generate email
            email_content = self.generate_email(
                user_profile=user_profile,
                startup=startup_info,
                match_rationale=match.rationale.dict(),
                relevant_projects=match.relevant_projects
            )
            
            # Update match with generated content
            match.email_body = email_content["email_body"]
            match.subject_line = email_content["subject_line"]
        
        return matches 