
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class OrderCreate(BaseModel):
    address_id: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name_snapshot: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    shipping_address_snapshot: dict
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]
