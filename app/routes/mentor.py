from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.auth import require_mentor
from app.db import get_db
from app.models.user import User
from app.models.mentor_apprentice import MentorApprentice
from app.models.assessment_draft import AssessmentDraft
from app.schemas.assessment_draft import AssessmentDraftOut
from app.models.user import User as UserModel
from fastapi import Query
from datetime import datetime

router = APIRouter()

@router.get("/my-apprentices", response_model=list[dict])
def list_apprentices(
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    apprentices = (
        db.query(MentorApprentice)
        .filter(MentorApprentice.mentor_id == current_user.id)
        .all()
    )

    apprentice_ids = [a.apprentice_id for a in apprentices]
    apprentice_users = (
        db.query(UserModel)
        .filter(UserModel.id.in_(apprentice_ids))
        .all()
    )

    return [
        {"id": u.id, "name": u.name, "email": u.email}
        for u in apprentice_users
    ]

@router.get("/apprentice/{apprentice_id}/draft", response_model=AssessmentDraftOut)
def get_apprentice_draft(
    apprentice_id: str,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    # Check if this apprentice belongs to the current mentor
    mapping = db.query(MentorApprentice).filter_by(
        mentor_id=current_user.id, apprentice_id=apprentice_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=403, detail="Not authorized to view this apprentice")

    draft = (
        db.query(AssessmentDraft)
        .filter_by(apprentice_id=apprentice_id, is_submitted=False)
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="No draft found for apprentice")

    return draft

from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentOut


@router.get("/apprentice/{apprentice_id}/submitted-assessments", response_model=list[AssessmentOut])
def get_submitted_assessments_for_apprentice(
    apprentice_id: str,
    category: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    # Verify mentor-apprentice relationship
    mapping = db.query(MentorApprentice).filter_by(
        mentor_id=current_user.id,
        apprentice_id=apprentice_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=403, detail="Not authorized to view this apprentice")

    query = db.query(Assessment).filter_by(apprentice_id=apprentice_id)

    if category:
        query = query.filter(Assessment.category == category)
    if start_date:
        query = query.filter(Assessment.created_at >= start_date)
    if end_date:
        query = query.filter(Assessment.created_at <= end_date)

    assessments = query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()
    return assessments

@router.get("/assessment/{assessment_id}", response_model=AssessmentOut)
def get_assessment_detail(
    assessment_id: str,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter_by(id=assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Check mentor-apprentice relationship
    mapping = db.query(MentorApprentice).filter_by(
        mentor_id=current_user.id,
        apprentice_id=assessment.apprentice_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=403, detail="Not authorized to view this assessment")

    return assessment