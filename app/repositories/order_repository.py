from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import OrderStatus
from app.models.order import Order


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["user", "courier"])
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.courier))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 10) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.courier))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_assigned_to_courier(self, courier_id: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.courier))
            .where(
                Order.courier_id == courier_id,
                Order.status.in_([OrderStatus.ACCEPTED, OrderStatus.DELIVERING]),
            )
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.status = status
        await self.session.flush()
        return order

    async def assign_courier(self, order_id: int, courier_id: int) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.courier_id = courier_id
        if order.status == OrderStatus.NEW:
            order.status = OrderStatus.ACCEPTED
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["user", "courier"])
        return order

    async def count_since(self, start: datetime) -> int:
        result = await self.session.execute(select(func.count(Order.id)).where(Order.created_at >= start))
        return int(result.scalar() or 0)

    async def revenue_between(self, start: datetime, end: datetime | None = None) -> int:
        query: Select[tuple[int | None]] = select(func.sum(Order.total_price)).where(
            Order.created_at >= start,
            Order.status != OrderStatus.CANCELED,
        )
        if end:
            query = query.where(Order.created_at < end)
        result = await self.session.execute(query)
        return int(result.scalar() or 0)
