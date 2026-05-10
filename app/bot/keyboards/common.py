from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.domain.enums import PaymentType, ProductType


def main_menu(is_admin: bool = False, is_courier: bool = False) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text="💧 Buyurtma berish")]]
    if is_courier:
        rows.append([KeyboardButton(text="🚚 Mening buyurtmalarim")])
    if is_admin:
        rows.append([KeyboardButton(text="🛠 Admin panel"), KeyboardButton(text="📊 Statistika")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Barcha buyurtmalar")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Kuryerlar")],
            [KeyboardButton(text="➕ Kuryer qo'shish")],
            [KeyboardButton(text="💧 Buyurtma berish")],
        ],
        resize_keyboard=True,
    )


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def product_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"💧 {ProductType.WATER_19L.value}")],
            [KeyboardButton(text=f"🔁 {ProductType.EMPTY_BOTTLE_EXCHANGE.value}")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def quantity_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
            [KeyboardButton(text="5"), KeyboardButton(text="10")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)],
            [KeyboardButton(text="⏭ Joylashuvsiz davom etish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Izohsiz davom etish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"💵 {PaymentType.CASH.value}")],
            [KeyboardButton(text=f"💳 {PaymentType.CARD_TRANSFER.value}")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Tasdiqlash")], [KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )
