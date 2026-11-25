from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import create_token
from datetime import timedelta
import os
from app.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Userlogin
from app.security import hash_password, verify_password
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def register_user(user:UserCreate,db:Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409,detail="The user already exists")
    user_data = user.model_dump()
    user_data["password_hash"] = hash_password(user_data.pop("password"))
    data = User(**user_data)
    db.add(data)
    db.commit()
    db.refresh(data)
    return {
        "message":f"Registration of {data.name} is done"
    }


def login_user(user:Userlogin, db: Session = Depends(get_db)):
    data = db.query(User).filter(User.email == user.email).first()
    if not data:
        raise HTTPException(status_code=401,detail="The user not found")
    if not verify_password(user.password, data.password_hash):
            raise HTTPException(status_code=401,detail="username or password is incorrect")
    token = create_token(
         {
              "sub":str(data.id)
         }, 
         timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), 
         "access"
         
        )
    return {
        "access_token": token,
        "token_type": "bearer"
        }