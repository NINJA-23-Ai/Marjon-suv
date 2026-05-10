from typing import Protocol


class StatsData(Protocol):
    today_orders_count: int
    today_revenue: int
    weekly_revenue: int
    monthly_revenue: int


def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def format_stats(stats: StatsData) -> str:
    return (
        "📊 Savdo statistikasi\n\n"
        f"Bugungi buyurtmalar soni: {stats.today_orders_count}\n"
        f"Bugungi tushum: {format_money(stats.today_revenue)}\n"
        f"Haftalik tushum: {format_money(stats.weekly_revenue)}\n"
        f"Oylik tushum: {format_money(stats.monthly_revenue)}"
    )
