from dataclasses import dataclass, field
from typing import List

from app.agents.llm import CareerResult, OpenAICompatibleClient, ResearchResult, TaskManagerResult


@dataclass
class TaskManagerAgent:
    name: str = "task_manager"
    description: str = "Creates and tracks the execution plan for the user workflow."
    capabilities: List[str] = field(default_factory=lambda: ["planning", "prioritization", "tracking"])

    def run(self, user_request: str) -> dict:
        return {
            "agent": self.name,
            "summary": "Created a task plan for the internship preparation workflow.",
            "tasks": [
                "Review internship requirements",
                "Compare resume with required skills",
                "Prepare application materials",
                "Schedule interview prep tasks",
            ],
            "status": "completed",
        }

    def run_with_llm(
        self,
        user_request: str,
        research: ResearchResult,
        career: CareerResult,
        client: OpenAICompatibleClient,
    ) -> TaskManagerResult:
        return client.run_task_manager(user_request, research, career)
