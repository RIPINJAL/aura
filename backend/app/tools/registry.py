from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ToolDefinition:
    name: str
    description: str
    permission: str = "read"
    risk_level: int = 0
    input_schema: Dict[str, str] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "search": ToolDefinition(
                name="search",
                description="Search for information across the web or internal knowledge base.",
                permission="read",
                risk_level=0,
                input_schema={"query": "string"},
            ),
            "calendar": ToolDefinition(
                name="calendar",
                description="Read or schedule calendar events when approved.",
                permission="read",
                risk_level=1,
                input_schema={"date": "string"},
            ),
            "docs": ToolDefinition(
                name="docs",
                description="Read and summarize personal documents or resumes.",
                permission="read",
                risk_level=0,
                input_schema={"document_id": "string"},
            ),
            "email": ToolDefinition(
                name="email",
                description="Draft emails for the user before submission.",
                permission="generate",
                risk_level=1,
                input_schema={"to": "string"},
            ),
        }

    def list_tools(self) -> List[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "permission": tool.permission,
                "risk_level": tool.risk_level,
                "input_schema": tool.input_schema,
            }
            for tool in self.tools.values()
        ]

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self.tools.get(name)
