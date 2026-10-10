import re

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.memory import Memory

STOP_WORDS = {
    "about", "after", "also", "and", "are", "can", "could", "from", "help", "into",
    "just", "make", "need", "please", "that", "the", "their", "them", "then", "this",
    "with", "would", "your",
}


def retrieve_relevant_context(
    user_request: str,
    db: Session,
    user_id: str,
    limit: int = 6,
) -> list[dict[str, str]]:
    terms = {
        term
        for term in re.findall(r"[a-z0-9]+", user_request.lower())
        if len(term) > 2 and term not in STOP_WORDS
    }
    if not terms:
        return []

    document_candidates: list[tuple[int, dict[str, str]]] = []
    documents = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .limit(100)
        .all()
    )
    for document in documents:
        searchable = f"{document.title} {document.source or ''} {document.content}".lower()
        score = sum(term in searchable for term in terms)
        if score:
            document_candidates.append((score, {
                "kind": "document",
                "title": document.title,
                "source": document.source or "",
                "content": document.content[:1500],
            }))

    memories = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(100)
        .all()
    )
    memory_candidates: list[tuple[int, dict[str, str]]] = []
    for memory in memories:
        searchable = f"{memory.type} {memory.content}".lower()
        score = sum(term in searchable for term in terms)
        if score:
            memory_candidates.append((score, {
                "kind": "memory",
                "title": memory.type,
                "source": "",
                "content": memory.content[:1500],
            }))

    document_candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    memory_candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    all_candidates = sorted(
        document_candidates + memory_candidates,
        key=lambda candidate: candidate[0],
        reverse=True,
    )
    per_kind_limit = max(1, limit // 2)
    selected = document_candidates[:per_kind_limit] + memory_candidates[:per_kind_limit]
    selected_ids = {id(context) for _, context in selected}
    selected.extend(
        candidate
        for candidate in all_candidates
        if id(candidate[1]) not in selected_ids
    )
    return [context for _, context in selected[:limit]]