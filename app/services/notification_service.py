from aiogram import Bot

from app.bot.keyboards.admin import admin_order_keyboard
from app.config.settings import Settings
from app.models.order import Order
from app.utils.formatting import format_order


class NotificationService:
    def __init__(self, bot: Bot, settings: Settings) -> None:
        self.bot = bot
        self.settings = settings

    async def notify_new_order(self, order: Order) -> None:
        await self.bot.send_message(
            self.settings.admin_chat_id,
            "🆕 <b>Yangi buyurtma tushdi!</b>\n\n" + format_order(order),
            reply_markup=admin_order_keyboard(order.id),
        )

    async def notify_courier_assigned(self, order: Order) -> None:
        if not order.courier:
            return
        await self.bot.send_message(
            order.courier.telegram_id,
            "🚚 <b>Sizga yangi buyurtma tayinlandi.</b>\n\n" + format_order(order),
        )
