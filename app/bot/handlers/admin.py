from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.utils.formatting import format_stats
from app.services.order_service import OrderService

router = Router(name="admin")


@router.message(F.text == "📊 Statistika")
async def stats(message: Message, session: AsyncSession, settings: Settings) -> None:
    if message.from_user.id not in settings.admin_ids:
        await message.answer("Bu bo'lim faqat adminlar uchun.")
        return
    sales_stats = await OrderService(session, settings).sales_stats()
    await message.answer(format_stats(sales_stats))
