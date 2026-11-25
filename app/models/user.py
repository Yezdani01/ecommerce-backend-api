from sqlalchemy import TIMESTAMP,Column, Integer, String, DateTime, text
from app.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password_hash = Column(String,nullable=False)
    phone = Column(String,nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )


