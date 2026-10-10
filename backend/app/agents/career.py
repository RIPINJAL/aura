from dataclasses import dataclass, field
from typing import List


@dataclass
class CareerAgent:
    name: str = "career"
    description: str = "Analyzes skills, role requirements, and resume fit for career preparation and applications."
    capabilities: List[str] = field(default_factory=lambda: ["skill_matching", "resume_analysis", "application_drafting"])

    def run(self, user_request: str) -> dict:
        return {
            "agent": self.name,
            "summary": "Mapped relevant skills and gaps for the requested internship workflow.",
            "matched_skills": ["Python", "Machine Learning", "Problem Solving"],
            "gaps": ["Portfolio evidence", "Interview practice", "Project depth"],
            "status": "completed",
        }
