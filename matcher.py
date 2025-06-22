import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple, Optional
import re
from data_models import UserProfile, Startup, MatchRationale, EmailMatch, MatchingConfig


class SemanticMatcher:
    def __init__(self, config: MatchingConfig = None):
        self.config = config or MatchingConfig()
        # Initialize sentence transformer for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better matching."""
        if not text:
            return ""
        # Remove special characters and normalize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_tech_stack_similarity(self, user_tech: List[str], startup_tech: List[str]) -> float:
        """Calculate tech stack similarity using exact matches and semantic similarity."""
        if not user_tech or not startup_tech:
            return 0.0
        
        # Normalize tech stack terms
        user_tech_normalized = [self._preprocess_text(tech) for tech in user_tech]
        startup_tech_normalized = [self._preprocess_text(tech) for tech in startup_tech]
        
        # Calculate exact matches
        exact_matches = len(set(user_tech_normalized) & set(startup_tech_normalized))
        exact_score = exact_matches / max(len(user_tech_normalized), len(startup_tech_normalized))
        
        # Calculate semantic similarity for non-exact matches
        if len(user_tech_normalized) > 0 and len(startup_tech_normalized) > 0:
            # Create embeddings for tech stacks
            user_tech_text = " ".join(user_tech_normalized)
            startup_tech_text = " ".join(startup_tech_normalized)
            
            embeddings = self.model.encode([user_tech_text, startup_tech_text])
            semantic_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Combine exact and semantic scores
            combined_score = 0.7 * exact_score + 0.3 * semantic_score
            return min(combined_score, 1.0)
        
        return exact_score
    
    def _extract_domain_similarity(self, user_profile: UserProfile, startup: Startup) -> float:
        """Calculate domain/industry similarity based on projects and startup description."""
        # Extract domain-related text from user projects
        user_domain_text = ""
        for project in user_profile.projects:
            user_domain_text += f" {project.description} {' '.join(project.outcomes)}"
        
        # Extract domain-related text from startup
        startup_domain_text = f"{startup.mission} {startup.product} {startup.description or ''}"
        
        if not user_domain_text.strip() or not startup_domain_text.strip():
            return 0.0
        
        # Calculate semantic similarity
        user_domain_clean = self._preprocess_text(user_domain_text)
        startup_domain_clean = self._preprocess_text(startup_domain_text)
        
        embeddings = self.model.encode([user_domain_clean, startup_domain_clean])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return max(0.0, similarity)
    
    def _extract_project_relevance(self, user_profile: UserProfile, startup: Startup) -> Tuple[float, List[str]]:
        """Calculate project relevance and return top relevant projects."""
        if not user_profile.projects:
            return 0.0, []
        
        project_scores = []
        
        for project in user_profile.projects:
            # Create project description
            project_text = f"{project.name} {project.description} {' '.join(project.tech_stack)} {' '.join(project.outcomes)}"
            
            # Create startup description
            startup_text = f"{startup.mission} {startup.product} {' '.join(startup.tech_stack)}"
            
            # Calculate semantic similarity
            project_clean = self._preprocess_text(project_text)
            startup_clean = self._preprocess_text(startup_text)
            
            embeddings = self.model.encode([project_clean, startup_clean])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            project_scores.append((project.name, similarity))
        
        # Sort by similarity score
        project_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top projects
        top_projects = [name for name, score in project_scores[:self.config.max_matches_per_company] if score > 0.3]
        avg_score = np.mean([score for _, score in project_scores[:self.config.max_matches_per_company]]) if project_scores else 0.0
        
        return avg_score, top_projects
    
    def _generate_rationale(self, tech_score: float, domain_score: float, project_score: float, 
                          relevant_projects: List[str], startup: Startup) -> List[str]:
        """Generate bullet-point rationale for the match."""
        rationale = []
        
        # Tech stack alignment
        if tech_score > 0.5:
            tech_overlap = len(set([tech.lower() for tech in startup.tech_stack]) & 
                             set([tech.lower() for project in startup.tech_stack for tech in startup.tech_stack]))
            if tech_overlap > 0:
                rationale.append(f"Tech stack alignment: {tech_overlap} matching technologies")
            else:
                rationale.append("Strong technical foundation with relevant technologies")
        
        # Domain alignment
        if domain_score > 0.6:
            rationale.append("Domain expertise aligns with company mission")
        elif domain_score > 0.4:
            rationale.append("Relevant experience in similar problem spaces")
        
        # Project relevance
        if relevant_projects:
            if len(relevant_projects) == 1:
                rationale.append(f"Direct project relevance: {relevant_projects[0]}")
            else:
                rationale.append(f"Multiple relevant projects: {', '.join(relevant_projects[:2])}")
        
        # Add startup-specific insights
        if startup.funding_stage:
            rationale.append(f"Experience with {startup.funding_stage} stage companies")
        
        if startup.team_size and startup.team_size < 50:
            rationale.append("Experience in early-stage, fast-paced environments")
        
        return rationale
    
    def calculate_match_score(self, user_profile: UserProfile, startup: Startup) -> Tuple[float, MatchRationale, List[str]]:
        """Calculate overall match score and rationale."""
        # Calculate individual scores
        tech_score = self._extract_tech_stack_similarity(
            [tech for project in user_profile.projects for tech in project.tech_stack] + user_profile.skills,
            startup.tech_stack
        )
        
        domain_score = self._extract_domain_similarity(user_profile, startup)
        project_score, relevant_projects = self._extract_project_relevance(user_profile, startup)
        
        # Calculate weighted overall score
        overall_score = (
            self.config.include_tech_stack_weight * tech_score +
            self.config.include_domain_weight * domain_score +
            self.config.include_project_weight * project_score
        )
        
        # Generate rationale
        rationale_points = self._generate_rationale(tech_score, domain_score, project_score, relevant_projects, startup)
        
        rationale = MatchRationale(
            tech_stack_alignment=tech_score,
            domain_alignment=domain_score,
            project_relevance=project_score,
            overall_score=overall_score,
            reasoning=rationale_points
        )
        
        return overall_score, rationale, relevant_projects
    
    def find_matches(self, user_profile: UserProfile, startups: List[Startup]) -> List[EmailMatch]:
        """Find all matches above the threshold score."""
        matches = []
        
        for startup in startups:
            score, rationale, relevant_projects = self.calculate_match_score(user_profile, startup)
            
            if score >= self.config.min_score_threshold:
                match = EmailMatch(
                    company_name=startup.company_name,
                    contact_email=startup.contact_email,
                    contact_name=startup.contact_name,
                    relevant_projects=relevant_projects,
                    rationale=rationale,
                    email_body="",  # Will be generated separately
                    subject_line="",  # Will be generated separately
                    match_score=score,
                    auto_send=False
                )
                matches.append(match)
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return matches
    
    def get_match_summary(self, matches: List[EmailMatch]) -> Dict:
        """Generate summary statistics for matches."""
        if not matches:
            return {
                "total_matches": 0,
                "average_score": 0.0,
                "score_distribution": {},
                "top_companies": []
            }
        
        scores = [match.match_score for match in matches]
        
        return {
            "total_matches": len(matches),
            "average_score": np.mean(scores),
            "score_distribution": {
                "high": len([s for s in scores if s >= 0.8]),
                "medium": len([s for s in scores if 0.6 <= s < 0.8]),
                "low": len([s for s in scores if s < 0.6])
            },
            "top_companies": [match.company_name for match in matches[:5]]
        } 