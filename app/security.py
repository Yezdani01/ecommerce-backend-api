from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ""
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is missing from .env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)

def create_token(data:dict,expires_delta:timedelta,token_type: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp":expire,
        "type": token_type
    })
    token = jwt.encode(to_encode,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)
    return token
