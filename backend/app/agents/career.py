from dataclasses import dataclass, field
from typing import List

from app.agents.llm import CareerResult, OpenAICompatibleClient, ResearchResult


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

    def run_with_llm(
        self,
        user_request: str,
        research: ResearchResult,
        client: OpenAICompatibleClient,
    ) -> CareerResult:
        return client.run_career(user_request, research)
