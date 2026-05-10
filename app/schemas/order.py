from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import OrderStatus, PaymentType, ProductType


class OrderCreate(BaseModel):
    user_id: int
    product: ProductType
    quantity: int = Field(ge=1, le=100)
    address: str = Field(min_length=5, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    comment: str | None = Field(default=None, max_length=1000)
    payment_type: PaymentType


class OrderRead(BaseModel):
    id: int
    user_id: int
    product: ProductType
    quantity: int
    address: str
    latitude: float | None
    longitude: float | None
    comment: str | None
    payment_type: PaymentType
    total_price: int
    status: OrderStatus
    courier_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SalesStats(BaseModel):
    today_orders_count: int
    today_revenue: int
    weekly_revenue: int
    monthly_revenue: int
