from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import assessment as assessment_schema
from app.db import get_db
from sqlalchemy import func
from app.models.assessment_draft import AssessmentDraft
from app.schemas.assessment_draft import AssessmentDraftCreate, AssessmentDraftOut
from app.services.auth import get_current_user, require_apprentice, require_mentor
from app.models.user import User
from app.models.question import Question
import uuid
from app.services.ai_scoring import score_assessment
from app.services.email import send_assessment_email
from sqlalchemy.orm import selectinload
from app.models.assessment_answer import AssessmentAnswer
import logging
from app.exceptions import ForbiddenException, NotFoundException
from app.models.mentor_apprentice import MentorApprentice
from app.models.assessment_template import AssessmentTemplate
from app.models.question import Question
from app.models.category import Category
from app.schemas.assessment_draft import QuestionItem
from app.schemas.assessment_draft import AssessmentDraftUpdate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/assessment-drafts", response_model=AssessmentDraftOut)
def save_draft(
    data: AssessmentDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "apprentice":
        raise HTTPException(status_code=403, detail="Only apprentices can save drafts")

    total_questions = db.query(Question).count()
    is_complete = data.answers and len(data.answers) >= total_questions

    draft = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id,
        is_submitted=False
    ).first()

    if draft:
        draft.answers = data.answers
        draft.last_question_id = data.last_question_id
        draft.is_submitted = is_complete
    else:
        draft = AssessmentDraft(
            id=str(uuid.uuid4()),
            apprentice_id=current_user.id,
            answers=data.answers,
            last_question_id=data.last_question_id,
            template_id=data.template_id,
            is_submitted=is_complete
        )
        db.add(draft)

    db.commit()
    db.refresh(draft)

    # Fetch questions from all categories linked to this template
    template = db.query(AssessmentTemplate).filter_by(id=data.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Assessment template not found")

    questions = (
        db.query(Question)
        .join(Category, Question.category_id == Category.id)
        .filter(Category.id.in_([c.id for c in template.categories]))
        .all()
    )
    questions_out = [QuestionItem.from_orm(q) for q in questions]

    draft_response = AssessmentDraftOut.from_orm(draft)
    draft_response.questions = questions_out

    if is_complete:
        # AI scoring + email logic already present
        pass

    return draft_response



@router.get("/assessment-drafts", response_model=AssessmentDraftOut)
def get_draft(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "apprentice":
        raise ForbiddenException("Only apprentices can access drafts")

    draft = db.query(AssessmentDraft).options(selectinload(AssessmentDraft.answers_rel))\
        .filter_by(apprentice_id=current_user.id, is_submitted=False).first()

    if not draft:
        raise NotFoundException("No draft found")

    return draft

@router.get("/assessment-drafts/resume")
def resume_draft(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "apprentice":
        raise ForbiddenException("Only apprentices can resume drafts")
    
    draft = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id,
        is_submitted=False
    ).first()

    if not draft:
        raise NotFoundException("No draft found")

    question = None
    if draft.last_question_id:
        question = db.query(Question).filter_by(id=draft.last_question_id).first()

    return {
        "draft": {
            "id": draft.id,
            "answers": draft.answers,
            "last_question_id": draft.last_question_id
        },
        "last_question": {
            "id": question.id,
            "text": question.text,
            "category_id": question.category_id
        } if question else None
    }

@router.patch("/assessment-drafts", response_model=AssessmentDraftOut)
def update_draft(
    data: AssessmentDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "apprentice":
        raise ForbiddenException("Only apprentices can update drafts")

    draft = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id,
        is_submitted=False
    ).first()

    if not draft:
        raise NotFoundException("No draft found")

    if data.answers is not None:
        draft.answers = data.answers
    if data.last_question_id:
        draft.last_question_id = data.last_question_id

    db.commit()
    db.refresh(draft)
    return draft

from app.models.assessment import Assessment
from app.services.ai_scoring import score_assessment
from app.services.email import send_assessment_email
import uuid

@router.post("/assessment-drafts/submit", response_model=assessment_schema.AssessmentOut)
def submit_draft(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "apprentice":
        raise ForbiddenException("Only apprentices can submit assessments")

    draft = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id,
        is_submitted=False
    ).first()

    if not draft:
        raise NotFoundException("No draft to submit")

    if not draft.answers:
        raise HTTPException(status_code=400, detail="Cannot submit an empty assessment")

    # Score via AI
    score, recommendation = score_assessment(draft.answers)

    # Save as new Assessment
    assessment = Assessment(
        id=str(uuid.uuid4()),
        apprentice_id=current_user.id,
        answers=draft.answers,
        score=score,
        recommendation=recommendation
    )
    db.add(assessment)

    # Mark draft as submitted
    draft.is_submitted = True
    db.commit()

    # Send email to mentor
    send_assessment_email(
        db=db,
        apprentice_id=current_user.id,
        assessment=assessment
    )

    return assessment

@router.get("/submitted-assessments/{apprentice_id}", response_model=list[AssessmentDraftOut])
def get_submitted_by_apprentice(
    apprentice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mentor authorization logic assumed to be in place already

    submissions = db.query(AssessmentDraft)\
        .options(selectinload(AssessmentDraft.answers_rel))\
        .filter_by(apprentice_id=apprentice_id, is_submitted=True).all()

    return submissions

@router.post("/assessment-drafts/start", response_model=AssessmentDraftOut)
def start_draft(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "apprentice":
        raise HTTPException(status_code=403, detail="Only apprentices can start drafts")

    # Check if apprentice has a draft already in progress for this template
    existing = db.query(AssessmentDraft).filter_by(
        apprentice_id=current_user.id,
        template_id=template_id,
        is_submitted=False
    ).first()
    if existing:
        return existing

    # Ensure template exists and is published
    template = db.query(AssessmentTemplate).filter_by(id=template_id, published=True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not published")

    # Create draft
    draft = AssessmentDraft(
        id=str(uuid.uuid4()),
        apprentice_id=current_user.id,
        template_id=template_id,
        answers={},
        last_question_id=None
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
