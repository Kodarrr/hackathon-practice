from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Education(BaseModel):
    degree: str
    institution: str
    year: str

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]

class ResumeData(BaseModel):
    name: str = "Not Mentioned"
    email: str = "Not Mentioned"
    phone: str = "Not Mentioned"
    education: List[Education] = []
    certifications: List[str] = []
    skills: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    programming_languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud_platforms: List[str] = []
    devops_tools: List[str] = []
    projects: List[Project] = []
    work_experience: List[str] = []
    experience_years: str = "Not Mentioned"
    awards: List[str] = []
    publications: List[str] = []
    languages: List[str] = []

class AnalysisResult(BaseModel):
    name: str
    email: str
    phone: str
    education: List[dict]
    experience_years: str
    skills: List[str]
    projects: List[dict]
    strengths: List[str]
    missing_skills: List[str]
    risk_flags: List[str]
    match_score: int
    recommendation: str
    human_review_required: bool
    confidence: float
