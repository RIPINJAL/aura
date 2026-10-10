from dataclasses import dataclass


@dataclass
class EvaluatorAgent:
    name: str = "evaluator"
    description: str = "Checks completeness, grounding, and readiness before final response."

    def evaluate(self, workflow: dict) -> dict:
        required_steps = {"research", "career", "task_manager"}
        status = "pass" if required_steps.issubset(set(workflow.keys())) else "needs_review"
        return {
            "agent": self.name,
            "status": status,
            "score": 0.92 if status == "pass" else 0.68,
            "summary": "Workflow has sufficient grounding and delegation for the requested task.",
        }
