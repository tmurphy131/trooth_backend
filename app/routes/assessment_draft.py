from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.assessment_draft import AssessmentDraft
from app.schemas.assessment_draft import AssessmentDraftCreate, AssessmentDraftOut
from app.services.auth import get_current_user, require_apprentice, require_mentor
from app.models.user import User
import uuid

router = APIRouter()

@router.post("/assessment-drafts", response_model=AssessmentDraftOut)
def save_draft(
    data: AssessmentDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_apprentice),
):
    if current_user.role != "apprentice":
        raise HTTPException(status_code=403, detail="Only apprentices can save drafts")

    existing = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id, is_submitted=False
    ).first()

    if existing:
        existing.answers = data.answers
        existing.last_question_id = data.last_question_id
        db.commit()
        db.refresh(existing)
        return existing

    draft = AssessmentDraft(
        id=str(uuid.uuid4()),
        apprentice_id=current_user.id,
        answers=data.answers,
        last_question_id=data.last_question_id
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft

@router.get("/assessment-drafts", response_model=AssessmentDraftOut)
def get_draft(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_apprentice),
):
    if current_user.role != "apprentice":
        raise HTTPException(status_code=403, detail="Only apprentices can access drafts")

    draft = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id, is_submitted=False
    ).first()

    if not draft:
        raise HTTPException(status_code=404, detail="No draft found")

    return draft
