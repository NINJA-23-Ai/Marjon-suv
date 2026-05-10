from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.domain.enums import OrderStatus, PaymentType, ProductType


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product: Mapped[ProductType] = mapped_column(Enum(ProductType, native_enum=False))
    quantity: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(500))
    payment_type: Mapped[PaymentType] = mapped_column(Enum(PaymentType, native_enum=False))
    total_price: Mapped[int] = mapped_column(Integer)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False), default=OrderStatus.NEW, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
