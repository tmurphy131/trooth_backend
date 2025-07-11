from fastapi import FastAPI
from app.routes import user, assessment
from app.config import init_firebase
from app.routes import mentor, assessment_draft, invite, question
from app.exceptions import UnauthorizedException, ForbiddenException, NotFoundException, ValidationException
from app.routes import admin_template
from dotenv import load_dotenv
import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.routes import admin_template
import logging
from app.routes import assessment_score_history
from app.routes import apprentices
from app.routes import mentor_notes


load_dotenv()  # Automatically loads from `.env`

# Optional: Confirm loading works
print("Loaded DB URL:", os.getenv("DATABASE_URL"))

app = FastAPI()

if os.getenv("ENV") != "test":
    init_firebase()

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(assessment.router, prefix="/assessments", tags=["Assessments"])
app.include_router(mentor.router, prefix="/mentor", tags=["Mentor"])
# app.include_router(assessment_draft.router, prefix="/assessment_draft", tags=["Assessment_draft"])
# app.include_router(invite.router, prefix="/invite", tags=["Invite"])
app.include_router(question.router, prefix="/question", tags=["Question"])
app.include_router(admin_template.router)
app.include_router(assessment_draft.router, prefix="/assessment-drafts")
app.include_router(invite.router, prefix="/invitations")
app.include_router(mentor.router)
app.include_router(assessment_score_history.router)
app.include_router(apprentices.router)
app.include_router(mentor_notes.router)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

@app.exception_handler(UnauthorizedException)
@app.exception_handler(ForbiddenException)
@app.exception_handler(NotFoundException)
@app.exception_handler(ValidationException)

async def handle_custom_exceptions(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/")
def root():
    return {"message": "T[root]H Assessment API"}