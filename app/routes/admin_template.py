from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth import require_admin, get_current_user
from app.models.assessment_template import AssessmentTemplate
from app.models.assessment_template_question import AssessmentTemplateQuestion
from app.models.question import Question
from app.schemas.assessment_template import (
    AssessmentTemplateCreate, AssessmentTemplateOut,
    AddQuestionToTemplate, FullTemplateView
)
from uuid import uuid4
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/admin/templates", tags=["Admin Templates"])

@router.post("", response_model=AssessmentTemplateOut, dependencies=[Depends(require_admin)])
def create_template(data: AssessmentTemplateCreate, db: Session = Depends(get_db)):
    template = AssessmentTemplate(**data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.post("/{template_id}/questions", dependencies=[Depends(require_admin)])
def add_question_to_template(
    template_id: str,
    item: AddQuestionToTemplate,
    db: Session = Depends(get_db)
):
    # Confirm template and question exist
    if not db.query(AssessmentTemplate).filter_by(id=template_id).first():
        raise HTTPException(status_code=404, detail="Template not found")
    if not db.query(Question).filter_by(id=item.question_id).first():
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check for duplicate
    existing = db.query(AssessmentTemplateQuestion).filter_by(
        template_id=template_id, question_id=item.question_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question already in template")

    link = AssessmentTemplateQuestion(
        template_id=template_id,
        question_id=item.question_id,
        order=item.order
    )
    db.add(link)
    db.commit()
    return {"message": "Question added"}

@router.get("", response_model=list[AssessmentTemplateOut], dependencies=[Depends(require_admin)])
def list_templates(db: Session = Depends(get_db)):
    return db.query(AssessmentTemplate).all()

@router.get("/{template_id}", response_model=FullTemplateView, dependencies=[Depends(require_admin)])
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(AssessmentTemplate).filter_by(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    links = db.query(AssessmentTemplateQuestion).filter_by(template_id=template_id).order_by(
        AssessmentTemplateQuestion.order
    ).all()

    question_list = [
        AddQuestionToTemplate(question_id=link.question_id, order=link.order)
        for link in links
    ]

    return FullTemplateView(
        id=template.id,
        name=template.name,
        description=template.description,
        is_published=template.is_published,
        questions=question_list
    )

@router.post("/{template_id}/clone")
def clone_assessment_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(get_current_user)
):
    template = db.query(AssessmentTemplate).filter(AssessmentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    new_template = AssessmentTemplate(
        id=str(uuid4()),
        name=f"{template.name} (Clone)",
        description=template.description,
        # 🔄 Only include the category if your model supports the relationship
        category_id=template.category_id  # or adjust as necessary
    )

    # Optional: if you have a many-to-many relationship to categories, clone them here
    # new_template.categories = template.categories[:]  # Only if `categories` is a defined relationship

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return {
        "id": new_template.id,
        "name": new_template.name,
        "description": new_template.description,
        "category_id": new_template.category_id,
    }