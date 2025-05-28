from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.db import get_db
from app.models.user import User
from app.models.mentor_apprentice import MentorApprentice
from app.models.apprentice_invitation import ApprenticeInvitation
from app.schemas.invite import InviteCreate, InviteAccept
from app.services.email import send_invitation_email

router = APIRouter()

@router.post("/invite-apprentice")
def invite_apprentice(invite: InviteCreate, db: Session = Depends(get_db)):
    mentor = db.query(User).filter_by(id=invite.mentor_id, role="mentor").first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    existing = db.query(ApprenticeInvitation).filter(
        ApprenticeInvitation.apprentice_email == invite.apprentice_email,
        ApprenticeInvitation.mentor_id == invite.mentor_id,
        ApprenticeInvitation.accepted == False,
        ApprenticeInvitation.expires_at > datetime.utcnow()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="An invitation is already pending for this apprentice")

    token = str(uuid.uuid4())
    invitation = ApprenticeInvitation(
        mentor_id=invite.mentor_id,
        apprentice_email=invite.apprentice_email,
        apprentice_name=invite.apprentice_name,
        token=token
    )
    db.add(invitation)
    db.commit()

    send_invitation_email(to_email=invite.apprentice_email, apprentice_name=invite.apprentice_name, token=token)
    return {"message": "Invitation sent"}


@router.post("/accept-invite")
def accept_invite(data: InviteAccept, db: Session = Depends(get_db)):
    invitation = db.query(ApprenticeInvitation).filter_by(token=data.token).first()
    if not invitation or invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation is invalid or expired")

    if invitation.accepted:
        raise HTTPException(status_code=400, detail="Invitation has already been accepted")

    # Check if apprentice user exists
    apprentice = db.query(User).filter_by(id=data.apprentice_id, role="apprentice").first()
    if not apprentice:
        raise HTTPException(status_code=404, detail="Apprentice not found")

    invitation.accepted = True
    relationship = MentorApprentice(
        mentor_id=invitation.mentor_id,
        apprentice_id=data.apprentice_id
    )
    db.add(relationship)
    db.commit()

    return {"message": "Invitation accepted, relationship created"}