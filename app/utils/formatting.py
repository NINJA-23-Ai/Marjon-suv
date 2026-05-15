from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.models.order import Order


class StatsData(Protocol):
    today_orders_count: int
    today_revenue: int
    weekly_revenue: int
    monthly_revenue: int


def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def format_stats(stats: StatsData) -> str:
    return (
        "📊 <b>Savdo statistikasi</b>\n\n"
        f"📦 Bugungi buyurtmalar soni: <b>{stats.today_orders_count}</b>\n"
        f"💰 Bugungi tushum: <b>{format_money(stats.today_revenue)}</b>\n"
        f"📆 Haftalik tushum: <b>{format_money(stats.weekly_revenue)}</b>\n"
        f"🗓 Oylik tushum: <b>{format_money(stats.monthly_revenue)}</b>"
    )


def location_text(order: "Order") -> str:
    if order.latitude is None or order.longitude is None:
        return "Joylashuv yuborilmagan"
    return f"https://maps.google.com/?q={order.latitude},{order.longitude}"


def format_order(order: "Order") -> str:
    courier = order.courier.name if order.courier else "Tayinlanmagan"
    comment = order.comment or "Yo'q"
    return (
        f"📦 <b>Buyurtma #{order.id}</b>\n\n"
        f"👤 Mijoz: <b>{order.user.name}</b>\n"
        f"📞 Telefon: <code>{order.user.phone}</code>\n"
        f"💧 Mahsulot: {order.product.value}\n"
        f"🔢 Miqdor: <b>{order.quantity}</b>\n"
        f"📍 Manzil: {order.address}\n"
        f"🗺 Joylashuv: {location_text(order)}\n"
        f"💬 Izoh: {comment}\n"
        f"💳 To'lov: {order.payment_type.value}\n"
        f"💰 Jami: <b>{format_money(order.total_price)}</b>\n"
        f"🚚 Kuryer: {courier}\n"
        f"🏷 Status: <b>{order.status.value}</b>"
    )


def format_customer(order: "Order") -> str:
    return (
        f"👤 <b>Buyurtmachi ma'lumoti</b>\n\n"
        f"Ism: <b>{order.user.name}</b>\n"
        f"Telefon: <code>{order.user.phone}</code>\n"
        f"Telegram ID: <code>{order.user.telegram_id}</code>\n"
        f"Manzil: {order.address}\n"
        f"Joylashuv: {location_text(order)}\n"
        f"Izoh: {order.comment or 'Yo\'q'}"
    )
