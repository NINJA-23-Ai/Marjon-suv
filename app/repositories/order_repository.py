from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["user"])
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self.session.get(Order, order_id)

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.status = status
        await self.session.flush()
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
