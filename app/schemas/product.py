
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class ProductCreate(BaseModel):
    category_id: int = Field(gt=0)
    sku: str = Field(min_length=2)
    name: str = Field(min_length=2)
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class ProductUpdate(BaseModel):
    category_id: int | None = Field(default=None, gt=0)
    sku: str | None = Field(default=None, min_length=2)
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class StockUpdate(BaseModel):
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    id: int
    category_id: int
    sku: str
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
