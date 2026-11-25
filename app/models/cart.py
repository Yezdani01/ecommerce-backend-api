
from sqlalchemy import (
    Column, Integer, ForeignKey,
    UniqueConstraint, CheckConstraint
)
from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"),
        nullable=False, unique=True
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id", "product_id",
            name="unique_cart_product"
        ),
        CheckConstraint(
            "quantity > 0",
            name="check_cart_quantity"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
