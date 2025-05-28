from fastapi import FastAPI
from app.routes import user, assessment
from app.config import init_firebase
from app.routes import mentor, assessment_draft, invite, question

app = FastAPI()

init_firebase()

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(assessment.router, prefix="/assessments", tags=["Assessments"])
app.include_router(mentor.router, prefix="/mentor", tags=["Mentor"])
app.include_router(assessment_draft.router, prefix="/assessment_draft", tags=["Assessment_draft"])
app.include_router(invite.router, prefix="/invite", tags=["Invite"])
app.include_router(question.router, prefix="/question", tags=["Question"])



@app.get("/")
def root():
    return {"message": "T[root]H Assessment API"}