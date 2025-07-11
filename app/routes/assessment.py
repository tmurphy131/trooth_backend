from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import assessment as assessment_schema
from app.models import assessment as assessment_model, user as user_model, mentor_apprentice as mentor_model
from app.db import get_db
from app.services.auth import verify_token
from app.services import ai_scoring
from app.services.email import send_assessment_email
from app.exceptions import ForbiddenException, NotFoundException
import uuid
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/", response_model=assessment_schema.AssessmentOut)
def create_assessment(
    assessment_input: assessment_schema.AssessmentCreate,
    db: Session = Depends(get_db),
    decoded_token=Depends(verify_token)
):
    try:
        user_id = decoded_token["uid"]
        if user_id != assessment_input.user_id:
            raise ForbiddenException("User ID does not match authenticated user.")

        apprentice = db.query(user_model.User).filter(user_model.User.id == user_id).first()
        if not apprentice:
            raise NotFoundException("User not found.")

        mentor_link = db.query(mentor_model.MentorApprentice).filter_by(apprentice_id=user_id).first()
        if not mentor_link:
            raise HTTPException(status_code=400, detail="No mentor relationship found.")

        mentor = db.query(user_model.User).filter_by(id=mentor_link.mentor_id).first()
        if not mentor:
            raise NotFoundException("Mentor not found.")

        ai_result = ai_scoring.score_assessment(assessment_input.answers)

        db_assessment = assessment_model.Assessment(
            id=str(uuid.uuid4()),
            title=assessment_input.title,
            user_id=user_id,
            score=ai_result.get("overall_score"),
            feedback=ai_result.get("summary_feedback")
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)

        send_assessment_email(
            to_email=mentor.email,
            apprentice_name=apprentice.name,
            assessment_title=assessment_input.title,
            score=ai_result.get("overall_score"),
            feedback_summary=ai_result.get("summary_feedback"),
            details=ai_result.get("details")
        )

        return db_assessment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
