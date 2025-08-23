from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.mentor_note import MentorNote
from app.models.assessment import Assessment
from app.models.mentor_apprentice import MentorApprentice
from app.schemas.mentor_note import MentorNoteCreate, MentorNoteOut
from app.services.auth import require_mentor
from app.models.user import User

router = APIRouter(prefix="/mentor-notes", tags=["Mentor Notes"])


@router.post("/", response_model=MentorNoteOut)
def create_mentor_note(
    note_data: MentorNoteCreate,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    # Verify the mentor is linked to the apprentice via the assessment
    assessment = db.query(Assessment).filter_by(id=note_data.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    mapping = db.query(MentorApprentice).filter_by(
        mentor_id=current_user.id,
        apprentice_id=assessment.apprentice_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=403, detail="Not authorized to comment on this assessment")

    note = MentorNote(
        assessment_id=note_data.assessment_id,
        mentor_id=current_user.id,
        content=note_data.content,
        follow_up_plan=note_data.follow_up_plan,
        is_private=note_data.is_private
    )

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/assessment/{assessment_id}", response_model=list[MentorNoteOut])
def list_mentor_notes_for_assessment(
    assessment_id: str,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    # Ensure the mentor is linked to this assessment
    assessment = db.query(Assessment).filter_by(id=assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    mapping = db.query(MentorApprentice).filter_by(
        mentor_id=current_user.id,
        apprentice_id=assessment.apprentice_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=403, detail="Not authorized")

    notes = db.query(MentorNote).filter_by(assessment_id=assessment_id).order_by(MentorNote.created_at.desc()).all()
    return notes


@router.delete("/{note_id}", status_code=204)
def delete_mentor_note(
    note_id: str,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db)
):
    note = db.query(MentorNote).filter_by(id=note_id, mentor_id=current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not owned by you")

    db.delete(note)
    db.commit()
    return