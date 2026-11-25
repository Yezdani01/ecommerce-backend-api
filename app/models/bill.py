
from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    Numeric, TIMESTAMP, text
)
from app.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer, ForeignKey("users.id"),
        nullable=False
    )

    order_id = Column(
        Integer, ForeignKey("orders.id"),
        nullable=False, unique=True
    )

    bill_number = Column(String, nullable=False, unique=True)

    subtotal = Column(Numeric(18, 2), nullable=False)
    delivery_fee = Column(Numeric(18, 2), nullable=False)
    final_total = Column(Numeric(18, 2), nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
