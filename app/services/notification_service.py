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

    async def notify_order_accepted(self, order: Order) -> None:
        await self.bot.send_message(
            order.user.telegram_id,
            f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
            f"Buyurtma raqami: <b>#{order.id}</b>\n"
            "Tez orada kuryer tayinlanadi va jarayon haqida xabar beramiz.",
        )

    async def notify_order_canceled(self, order: Order) -> None:
        await self.bot.send_message(
            order.user.telegram_id,
            f"❌ <b>Buyurtmangiz rad etildi.</b>\n\n"
            f"Buyurtma raqami: <b>#{order.id}</b>\n"
            "Qo'shimcha ma'lumot uchun operator bilan bog'laning.",
        )

    async def notify_admin_order_decision(self, order: Order, *, accepted: bool, admin_name: str) -> None:
        action = "qabul qildi" if accepted else "rad etdi"
        emoji = "✅" if accepted else "❌"
        await self.bot.send_message(
            self.settings.admin_chat_id,
            f"{emoji} <b>Admin {admin_name} buyurtma #{order.id} ni {action}.</b>\n\n"
            + format_order(order),
        )

    async def notify_admin_courier_assigned(self, order: Order, *, admin_name: str) -> None:
        if not order.courier:
            return
        await self.bot.send_message(
            self.settings.admin_chat_id,
            f"🚚 <b>Admin {admin_name} buyurtma #{order.id} ga {order.courier.name} kuryerni tayinladi.</b>\n\n"
            + format_order(order),
        )

    async def notify_courier_assigned(self, order: Order) -> None:
        if not order.courier:
            return
        await self.bot.send_message(
            order.courier.telegram_id,
            "🚚 <b>Sizga yangi buyurtma tayinlandi.</b>\n\n" + format_order(order),
        )
        await self.bot.send_message(
            order.user.telegram_id,
            f"🚚 <b>Buyurtmangizga kuryer tayinlandi.</b>\n\n"
            f"Buyurtma: <b>#{order.id}</b>\n"
            f"Kuryer: <b>{order.courier.name}</b>\n"
            f"Telefon: <code>{order.courier.phone}</code>",
        )

    async def notify_order_delivering(self, order: Order) -> None:
        await self.bot.send_message(
            order.user.telegram_id,
            f"🚚 <b>Kuryer yo'lga chiqdi!</b>\n\n"
            f"Buyurtma: <b>#{order.id}</b>\n"
            "Iltimos, telefoningiz yoqilgan bo'lsin.",
        )
        await self.bot.send_message(
            self.settings.admin_chat_id,
            "🚚 <b>Kuryer yo'lga chiqdi.</b>\n\n" + format_order(order),
        )

    async def notify_order_delivered(self, order: Order) -> None:
        await self.bot.send_message(
            order.user.telegram_id,
            f"✅ <b>Buyurtmangiz yetkazildi.</b>\n\n"
            f"Buyurtma: <b>#{order.id}</b>\n"
            "💙 Xaridingiz uchun rahmat! Yana kutib qolamiz.",
        )
        await self.bot.send_message(
            self.settings.admin_chat_id,
            "✅ <b>Buyurtma yetkazib berildi.</b>\n\n" + format_order(order),
        )
