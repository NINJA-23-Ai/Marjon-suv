from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.order import Order
from app.models.user import User


def admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"admin:accept:{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin:cancel:{order_id}"),
            ],
            [InlineKeyboardButton(text="🚚 Kuryer tayinlash", callback_data=f"admin:assign:{order_id}")],
            [InlineKeyboardButton(text="👤 Buyurtmachi", callback_data=f"admin:customer:{order_id}")],
        ]
    )


def order_list_keyboard(orders: list[Order]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"#{order.id} • {order.status.value}", callback_data=f"admin:view:{order.id}")]
        for order in orders
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons or [[InlineKeyboardButton(text="Buyurtma yo'q", callback_data="noop")]])


def courier_select_keyboard(order_id: int, couriers: list[User]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"🚚 {courier.name}", callback_data=f"admin:setcourier:{order_id}:{courier.id}")]
        for courier in couriers
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"admin:view:{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def courier_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚚 Yo'lga chiqdim", callback_data=f"courier:delivering:{order_id}")],
            [InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"courier:delivered:{order_id}")],
            [InlineKeyboardButton(text="👤 Mijoz ma'lumoti", callback_data=f"courier:customer:{order_id}")],
        ]
    )
