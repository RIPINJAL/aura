from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["browser"])

ALLOWED_DOMAINS = [
    "localhost",
    "127.0.0.1",
    "example.com",
    "github.com",
    "docs.github.com",
]


@router.get("/browser/status")
def browser_status():
    return {
        "status": "ready",
        "mode": "simulated",
        "allowed_domains": ALLOWED_DOMAINS,
        "notes": "Browser automation is restricted to a safe allowlist and requires approval for sensitive actions.",
    }


@router.post("/browser/safe-visit")
def safe_visit(payload: dict):
    url = str(payload.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    allowed = any(host == domain or host.endswith(f".{domain}") for domain in ALLOWED_DOMAINS)

    if not allowed:
        return JSONResponse(
            status_code=403,
            content={
                "allowed": False,
                "reason": "Domain is not on the safe allowlist",
                "url": url,
                "status": "blocked",
            },
        )

    return {
        "allowed": True,
        "status": "approved",
        "url": url,
        "host": host,
    }
