from aiogram import Bot

from app.config.settings import Settings
from app.models.order import Order
from app.utils.formatting import format_money


class NotificationService:
    def __init__(self, bot: Bot, settings: Settings) -> None:
        self.bot = bot
        self.settings = settings

    async def notify_new_order(self, order: Order) -> None:
        text = (
            "🆕 Yangi buyurtma\n\n"
            f"Buyurtma ID: #{order.id}\n"
            f"Mijoz: {order.user.name}\n"
            f"Telefon: {order.user.phone}\n"
            f"Mahsulot: {order.product.value}\n"
            f"Miqdor: {order.quantity}\n"
            f"Manzil: {order.address}\n"
            f"To'lov: {order.payment_type.value}\n"
            f"Jami: {format_money(order.total_price)}\n"
            f"Status: {order.status.value}"
        )
        await self.bot.send_message(self.settings.admin_chat_id, text)
