from types import SimpleNamespace

from app.domain.enums import ProductType
from app.utils.formatting import format_money, format_stats
from app.services.pricing import PricingService


def test_pricing_service_calculates_total() -> None:
    settings = SimpleNamespace(water_19l_price=15000, empty_bottle_exchange_price=0)
    service = PricingService(settings)  # type: ignore[arg-type]

    assert service.total(ProductType.WATER_19L, 3) == 45000
    assert service.total(ProductType.EMPTY_BOTTLE_EXCHANGE, 5) == 0


def test_format_stats_uzbek_text() -> None:
    stats = SimpleNamespace(
        today_orders_count=2,
        today_revenue=30000,
        weekly_revenue=120000,
        monthly_revenue=500000,
    )

    text = format_stats(stats)

    assert "Bugungi buyurtmalar soni: 2" in text
    assert "Bugungi tushum: 30 000 so'm" in text
    assert format_money(500000) == "500 000 so'm"
