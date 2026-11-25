
from pydantic import BaseModel, Field, ConfigDict


class AddressCreate(BaseModel):
    address_line_1: str = Field(min_length=3)
    address_line_2: str | None = None
    city: str
    state: str
    postal_code: str = Field(min_length=6, max_length=10)


class AddressUpdate(BaseModel):
    address_line_1: str | None = Field(default=None, min_length=3)
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = Field(default=None, min_length=6, max_length=10)


class AddressResponse(BaseModel):
    id: int
    user_id: int
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    postal_code: str

    model_config = ConfigDict(from_attributes=True)
