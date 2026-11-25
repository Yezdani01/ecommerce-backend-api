from app.database import session_local
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from app.security import JWT_SECRET_KEY, JWT_ALGORITHM
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_db():
    # Create a database session
    db = session_local()
    try:
        yield(db)
    finally:
        db.close()
    # Yield the session
    # Close the session afterward


# def get_current_user(
#     authorization: str = Header(...),
#     db: Session = Depends(get_db)
# ):
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID")

    current_user = db.query(User).filter(User.id == user_id).first()

    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")

    return current_user



# curl -X GET "http://127.0.0.1:8000/api/v1/users/me" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzk1NTMzNTU5LCJ0eXBlIjoiYWNjZXNzIn0.SMgXcvaC6tnUg0_0YKMSkjHdnnX4oH3t9v1Yupppbnw"