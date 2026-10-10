from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["security"])

PROMPT_INJECTION_PATTERNS = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "act as",
    "you are now",
    "send the api key",
    "send credentials",
    "developer mode",
    "override safety",
    "system prompt",
    "attacker.com",
]


@router.post("/security/check")
def security_check(payload: dict):
    text = str(payload.get("text") or "").lower()
    matches = [pattern for pattern in PROMPT_INJECTION_PATTERNS if pattern in text]
    risk_level = min(5, max(1, len(matches) + 1))
    blocked = risk_level >= 2 or bool(matches)

    return {
        "risk_level": risk_level,
        "blocked": blocked,
        "matched_patterns": matches,
        "message": "Prompt injection or unsafe instruction detected." if blocked else "Input appears safe.",
    }
