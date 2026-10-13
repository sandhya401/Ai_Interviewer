
from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeProject(BaseModel):
    name: str = Field(description="Project name, if available.")
    description: str = Field(
        description="Short summary grounded in the resume."
    )
    technologies: List[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    candidate_name: Optional[str] = None
    professional_summary: str = ""
    total_experience: str = ""
    skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    projects: List[ResumeProject] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    potential_interview_topics: List[str] = Field(default_factory=list)
    missing_or_unclear_information: List[str] = Field(
        default_factory=list
    )
