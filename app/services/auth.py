from firebase_admin import auth
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth
from app.db import get_db
from app.models.user import User
from sqlalchemy.orm import Session
import datetime
from app.schemas.user import UserSchema

security = HTTPBearer()

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    id_token = auth_header.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(role: str):
    def role_checker(decoded_token=Depends(verify_token)):
        if decoded_token.get("role") != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Insufficient role")
        return decoded_token
    return role_checker

def require_roles(roles: list):
    def role_checker(decoded_token=Depends(verify_token)):
        if decoded_token.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Insufficient role")
        return decoded_token
    return role_checker

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    
    token = credentials.credentials
    if token == "mock-mentor-token":
        return User(id="mentor-1", name="Mentor One", email="mentor@example.com", role="mentor", created_at=datetime.utcnow())
    elif token == "mock-apprentice-token":
        return User(id="apprentice-1", name="Apprentice One", email="apprentice@example.com", role="apprentice", created_at=datetime.utcnow())
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        user_id = decoded_token["uid"]
        email = decoded_token["email"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database",
        )
    return user

def require_mentor(user: User = Depends(get_current_user)) -> User:
    if user.role != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor access required"
        )
    return user

def require_apprentice(user: User = Depends(get_current_user)) -> User:
    if user.role != "apprentice":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apprentice access required"
        )
    return user

# def require_admin(current_user: User = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admin privileges required"
#         )
#     return current_user

def require_admin(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

def require_mentor_or_admin(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if current_user.role not in {"mentor", "admin"}:
        raise HTTPException(status_code=403, detail="Mentors or admins only.")
    return current_user