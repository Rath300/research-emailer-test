from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum


class FundingStage(str, Enum):
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B = "Series B"
    SERIES_C = "Series C"
    YC = "Y Combinator"
    OTHER = "Other"


class Project(BaseModel):
    name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Brief description of the project")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    outcomes: List[str] = Field(default_factory=list, description="Key outcomes and metrics")
    duration: Optional[str] = Field(None, description="Project duration")
    role: Optional[str] = Field(None, description="Your role in the project")


class UserProfile(BaseModel):
    name: str = Field(..., description="Your full name")
    title: str = Field(..., description="Your professional title")
    email: EmailStr = Field(..., description="Your email address")
    projects: List[Project] = Field(default_factory=list, description="List of your projects")
    skills: List[str] = Field(default_factory=list, description="Your technical skills")
    experience: str = Field(..., description="Brief summary of your experience")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")


class Startup(BaseModel):
    company_name: str = Field(..., description="Name of the startup")
    mission: str = Field(..., description="Company mission statement")
    product: str = Field(..., description="Product description")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    team_size: Optional[int] = Field(None, description="Number of employees")
    funding_stage: Optional[FundingStage] = Field(None, description="Funding stage")
    website: Optional[str] = Field(None, description="Company website")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_name: Optional[str] = Field(None, description="Contact person name")
    location: Optional[str] = Field(None, description="Company location")
    industry: Optional[str] = Field(None, description="Industry/domain")
    description: Optional[str] = Field(None, description="Additional description")


class MatchRationale(BaseModel):
    tech_stack_alignment: float = Field(..., description="Tech stack similarity score (0-1)")
    domain_alignment: float = Field(..., description="Domain/industry alignment score (0-1)")
    project_relevance: float = Field(..., description="Project relevance score (0-1)")
    overall_score: float = Field(..., description="Overall match score (0-1)")
    reasoning: List[str] = Field(default_factory=list, description="Bullet points explaining the match")


class EmailMatch(BaseModel):
    company_name: str = Field(..., description="Name of the startup")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    contact_name: Optional[str] = Field(None, description="Contact person name")
    relevant_projects: List[str] = Field(default_factory=list, description="Relevant project names")
    rationale: MatchRationale = Field(..., description="Match rationale and scores")
    email_body: str = Field(..., description="Generated email content")
    subject_line: str = Field(..., description="Email subject line")
    match_score: float = Field(..., description="Overall match score (0-1)")
    auto_send: bool = Field(default=False, description="Whether to auto-send this email")


class EmailBatch(BaseModel):
    user_profile: UserProfile = Field(..., description="User profile information")
    matches: List[EmailMatch] = Field(default_factory=list, description="List of email matches")
    total_matches: int = Field(..., description="Total number of matches")
    average_score: float = Field(..., description="Average match score")
    generated_at: str = Field(..., description="Timestamp of generation")


class EmailConfig(BaseModel):
    smtp_host: str = Field(..., description="SMTP server host")
    smtp_port: int = Field(..., description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")
    from_name: str = Field(..., description="Sender name")
    from_email: str = Field(..., description="Sender email")
    reply_to: Optional[str] = Field(None, description="Reply-to email address")


class MatchingConfig(BaseModel):
    min_score_threshold: float = Field(default=0.6, description="Minimum score to consider a match")
    max_matches_per_company: int = Field(default=3, description="Maximum projects to match per company")
    include_tech_stack_weight: float = Field(default=0.4, description="Weight for tech stack matching")
    include_domain_weight: float = Field(default=0.3, description="Weight for domain matching")
    include_project_weight: float = Field(default=0.3, description="Weight for project relevance")
    email_tone: str = Field(default="confident", description="Email tone: confident, professional, casual")
    email_length: str = Field(default="concise", description="Email length: concise, detailed, brief") 