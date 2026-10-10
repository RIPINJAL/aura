from dataclasses import dataclass, field
from typing import List

from app.agents.career import CareerAgent
from app.agents.context import retrieve_relevant_context
from app.agents.evaluator import EvaluatorAgent
from app.agents.llm import LLMProviderError, OpenAICompatibleClient
from app.agents.research import ResearchAgent
from app.agents.task_manager import TaskManagerAgent
from app.core.config import get_settings


@dataclass
class SupervisorAgent:
    name: str = "supervisor"
    description: str = "Coordinates the workflow, decomposes tasks, and delegates execution."
    capabilities: List[str] = field(
        default_factory=lambda: [
            "planning",
            "delegation",
            "coordination",
            "evaluation",
            "recovery",
        ]
    )

    def plan(self, user_request: str) -> List[str]:
        return [
            "Understand the user objective",
            "Break it into actionable steps",
            "Determine required agents and tools",
            "Assign execution order",
            "Review results and decide final output",
            f"Request approval when the request requires sensitive action: {user_request}",
        ]

    def run(self, user_request: str, context: list[dict[str, str]] | None = None) -> dict:
        settings = get_settings()
        if settings.llm_base_url and settings.llm_model:
            generated = OpenAICompatibleClient(settings).generate_workflow(user_request, context)
            workflow = generated.model_dump(exclude={"summary", "plan"})
            summary = generated.summary
            plan = generated.plan
            mode = "llm"
        else:
            workflow = {
                "research": ResearchAgent().run(user_request),
                "career": CareerAgent().run(user_request),
                "task_manager": TaskManagerAgent().run(user_request),
            }
            summary = "Supervisor is using the built-in demo workflow. Configure an LLM provider to enable generated results."
            plan = self.plan(user_request)
            mode = "demo"
        evaluator = EvaluatorAgent().evaluate(workflow)

        return {
            "agent": self.name,
            "summary": summary,
            "plan": plan,
            "workflow": workflow,
            "evaluation": evaluator,
            "status": "completed",
            "mode": mode,
            "context_used": [
                f"{item['kind']}: {item['title']}" for item in (context or [])
            ] if mode == "llm" else [],
        }
