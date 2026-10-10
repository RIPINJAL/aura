from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    documents = db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).all()
    return documents


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db_document = Document(
        user_id=user.id,
        title=document.title,
        content=document.content,
        source=document.source,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == user.id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/documents/search")
def search_documents(payload: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = (payload.get("query") or "").lower().strip()
    if not query:
        return {"results": []}

    documents = db.query(Document).filter(Document.user_id == user.id).all()
    results = []
    for doc in documents:
        if query in doc.title.lower() or query in doc.content.lower():
            results.append({
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "match": "keyword",
            })

    return {"results": results}
