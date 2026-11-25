
from pydantic import BaseModel, Field
from decimal import Decimal


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, strict=True)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, strict=True)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    is_active: bool


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total: Decimal
