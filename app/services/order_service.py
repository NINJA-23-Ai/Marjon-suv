from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.domain.enums import OrderStatus
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, SalesStats
from app.services.pricing import PricingService


class OrderService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.orders = OrderRepository(session)
        self.pricing = PricingService(settings)

    async def create_order(self, data: OrderCreate) -> Order:
        total_price = self.pricing.total(data.product, data.quantity)
        order = Order(
            user_id=data.user_id,
            product=data.product,
            quantity=data.quantity,
            address=data.address.strip(),
            latitude=data.latitude,
            longitude=data.longitude,
            comment=data.comment.strip() if data.comment else None,
            payment_type=data.payment_type,
            total_price=total_price,
            status=OrderStatus.NEW,
        )
        return await self.orders.create(order)

    async def get_order(self, order_id: int) -> Order | None:
        return await self.orders.get_by_id(order_id)

    async def list_recent_orders(self, limit: int = 10) -> list[Order]:
        return await self.orders.list_recent(limit)

    async def list_courier_orders(self, courier_id: int) -> list[Order]:
        return await self.orders.list_assigned_to_courier(courier_id)

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        return await self.orders.update_status(order_id, status)

    async def assign_courier(self, order_id: int, courier_id: int) -> Order | None:
        return await self.orders.assign_courier(order_id, courier_id)

    async def sales_stats(self) -> SalesStats:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        return SalesStats(
            today_orders_count=await self.orders.count_since(today_start),
            today_revenue=await self.orders.revenue_between(today_start),
            weekly_revenue=await self.orders.revenue_between(week_start),
            monthly_revenue=await self.orders.revenue_between(month_start),
        )
