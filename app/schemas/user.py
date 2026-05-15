from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: int
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(pattern=r"^\+?\d{9,15}$")


class UserRead(BaseModel):
    id: int
    telegram_id: int
    name: str
    phone: str

    model_config = {"from_attributes": True}
