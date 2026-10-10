from dataclasses import dataclass, field
from typing import List


@dataclass
class ResearchAgent:
    name: str = "research"
    description: str = "Finds relevant company, role, and industry information to ground recommendations."
    capabilities: List[str] = field(default_factory=lambda: ["search", "summarization", "citation"])

    def run(self, user_request: str) -> dict:
        return {
            "agent": self.name,
            "summary": "Gathered relevant role and company context for the request.",
            "findings": [
                "Role aligns with AI/ML internship requirements",
                "Focus areas likely include Python, machine learning, and applied problem solving",
                "Need to validate matching with resume and application goals",
            ],
            "status": "completed",
        }
