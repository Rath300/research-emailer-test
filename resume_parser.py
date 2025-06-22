"""
📄 Resume Parser for AI Cold Outreach System
Extracts profile information from uploaded resumes
"""

import os
import json
import re
from typing import Dict, List, Any
from pathlib import Path

def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats"""
    try:
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # For now, only support .txt files to avoid additional dependencies
            return f"Please convert your resume to .txt format. Supported: .txt"
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

def parse_resume_with_ai(resume_text: str, openai_client=None) -> Dict[str, Any]:
    """Parse resume using AI if available, otherwise use pattern matching"""
    
    if openai_client:
        return _ai_parse_resume(resume_text, openai_client)
    else:
        return _pattern_parse_resume(resume_text)

def _ai_parse_resume(resume_text: str, openai_client) -> Dict[str, Any]:
    """Use OpenAI to parse resume intelligently"""
    try:
        prompt = f"""
        Parse this resume and extract the following information in JSON format:
        
        Resume Text:
        {resume_text[:3000]}
        
        Extract:
        1. name: Full name of the person
        2. email: Email address
        3. skills: List of technical skills (programming languages, frameworks, tools)
        4. experience: Years of experience or experience summary
        5. current_role: Current job title or seeking role
        6. education: Highest degree or relevant education
        7. summary: Brief professional summary (2-3 sentences)
        8. projects: List of 3-5 key projects with brief descriptions
        
        Return ONLY a valid JSON object with these fields.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            parsed_data = json.loads(result)
            return _validate_parsed_data(parsed_data)
        except json.JSONDecodeError:
            return _pattern_parse_resume(resume_text)
            
    except Exception as e:
        print(f"AI parsing failed: {e}")
        return _pattern_parse_resume(resume_text)

def _pattern_parse_resume(resume_text: str) -> Dict[str, Any]:
    """Parse resume using pattern matching and keyword extraction"""
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text)
    email = emails[0] if emails else "developer@example.com"
    
    # Extract name (first line that looks like a name)
    lines = resume_text.split('\n')
    name = "Professional Developer"
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) <= 4 and '@' not in line and not any(char.isdigit() for char in line):
            if len(line) > 5:
                name = line
                break
    
    # Extract skills using common technical keywords
    skills_keywords = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
        'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
        'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch',
        'rest api', 'graphql', 'microservices', 'agile', 'scrum'
    ]
    
    found_skills = []
    resume_lower = resume_text.lower()
    for skill in skills_keywords:
        if skill in resume_lower:
            found_skills.append(skill.title())
    
    skills = list(set(found_skills))[:15] if found_skills else ['Python', 'Web Development']
    
    # Extract experience years
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*in',
        r'experience\s*:\s*(\d+)\+?\s*years?'
    ]
    
    experience = "5+ years of experience"
    for pattern in experience_patterns:
        matches = re.findall(pattern, resume_lower)
        if matches:
            years = matches[0]
            experience = f"{years}+ years of experience"
            break
    
    # Extract current role
    job_titles = [
        'software engineer', 'developer', 'programmer', 'architect', 'manager',
        'analyst', 'consultant', 'specialist', 'lead', 'senior', 'principal',
        'data scientist', 'ml engineer', 'devops', 'full stack', 'frontend', 'backend'
    ]
    
    current_role = "Software Developer"
    for title in job_titles:
        if title in resume_lower:
            current_role = title.title()
            break
    
    # Extract education
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'bs', 'ms', 'mba']
    education = "Computer Science Degree"
    for keyword in education_keywords:
        if keyword in resume_lower:
            for line in lines:
                if keyword in line.lower():
                    education = line.strip()[:100]
                    break
            break
    
    # Extract projects
    projects = []
    project_keywords = ['project', 'built', 'developed', 'created', 'designed', 'implemented']
    
    # Look for project sections
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in project_keywords):
            # Check if this looks like a project description
            if len(line.strip()) > 20 and ('app' in line_lower or 'system' in line_lower or 'platform' in line_lower or 'tool' in line_lower or 'website' in line_lower or 'api' in line_lower):
                projects.append(line.strip()[:150])
                if len(projects) >= 5:
                    break
    
    # If no projects found, create some based on skills
    if not projects:
        if 'Python' in skills or 'python' in resume_lower:
            projects.append("Python automation scripts and data processing tools")
        if 'React' in skills or 'react' in resume_lower:
            projects.append("React web applications with modern UI/UX")
        if 'API' in resume_lower or 'rest' in resume_lower:
            projects.append("RESTful API development and integration")
        if 'Database' in resume_lower or any(db in resume_lower for db in ['sql', 'mongodb', 'postgresql']):
            projects.append("Database design and optimization projects")
        if 'Machine Learning' in skills or 'ai' in resume_lower:
            projects.append("Machine learning models and AI applications")
    
    # Ensure we have at least 3 projects
    if len(projects) < 3:
        projects.extend([
            "Full-stack web application development",
            "Cloud infrastructure and deployment automation",
            "Open-source contributions and collaborative coding"
        ])
    
    return {
        'name': name,
        'email': email,
        'skills': skills,
        'experience': experience,
        'current_role': current_role,
        'education': education,
        'summary': f"Experienced {current_role.lower()} with {experience.lower()} in software development",
        'projects': projects[:5]  # Limit to 5 projects
    }

def _validate_parsed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean parsed resume data"""
    
    required_fields = ['name', 'email', 'skills', 'experience', 'current_role', 'education', 'summary', 'projects']
    for field in required_fields:
        if field not in data:
            if field == 'projects':
                data[field] = ["Full-stack web development", "API integration", "Database design"]
            else:
                data[field] = "Not specified"
    
    if isinstance(data['skills'], str):
        data['skills'] = [skill.strip() for skill in data['skills'].split(',')]
    
    if isinstance(data['projects'], str):
        data['projects'] = [proj.strip() for proj in data['projects'].split(',')]
    
    if len(data['skills']) > 20:
        data['skills'] = data['skills'][:20]
        
    if len(data['projects']) > 5:
        data['projects'] = data['projects'][:5]
    
    for key, value in data.items():
        if not value or value == "null" or value == "None":
            if key == 'projects':
                data[key] = ["Full-stack web development", "API integration", "Database design"]
            else:
                data[key] = "Not specified"
    
    return data

def save_user_profile(profile_data: Dict[str, Any], config_file: str = 'local_config.py') -> bool:
    """Save parsed profile data to local config"""
    try:
        config_content = ""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_content = f.read()
        
        new_profile = f'''
# User Profile (Updated from Resume)
USER_NAME = "{profile_data['name']}"
USER_EMAIL = "{profile_data['email']}"
USER_SKILLS = {profile_data['skills']}
USER_EXPERIENCE = "{profile_data['experience']}"
USER_CURRENT_ROLE = "{profile_data['current_role']}"
USER_EDUCATION = "{profile_data['education']}"
USER_SUMMARY = "{profile_data['summary']}"
USER_PROJECTS = {profile_data['projects']}
'''
        
        lines = config_content.split('\n')
        new_lines = []
        skip_section = False
        
        for line in lines:
            if line.strip().startswith('# User Profile'):
                skip_section = True
                continue
            elif skip_section and line.strip().startswith('USER_'):
                continue
            elif skip_section and (line.strip() == '' or line.strip().startswith('#')):
                if not line.strip().startswith('USER_'):
                    skip_section = False
                    new_lines.append(line)
            else:
                skip_section = False
                new_lines.append(line)
        
        updated_content = '\n'.join(new_lines) + new_profile
        
        with open(config_file, 'w') as f:
            f.write(updated_content)
        
        return True
        
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def get_supported_formats() -> List[str]:
    """Get list of supported resume file formats"""
    return ['.txt']

# Example usage and testing
if __name__ == "__main__":
    # Test with sample resume text
    sample_resume = """
    John Doe
    john.doe@email.com
    
    EXPERIENCE
    Senior Software Engineer with 5+ years of experience in full-stack development.
    
    SKILLS
    - Python, JavaScript, React, Node.js
    - AWS, Docker, PostgreSQL
    - Machine Learning, TensorFlow
    
    EDUCATION
    Bachelor of Science in Computer Science
    """
    
    result = _pattern_parse_resume(sample_resume)
    print("Parsed Resume:")
    print(json.dumps(result, indent=2)) 