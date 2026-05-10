from types import SimpleNamespace

from app.config.database_url import DatabaseUrlError, normalize_database_url
from app.domain.enums import ProductType
from app.services.pricing import PricingService
from app.utils.formatting import format_money, format_stats


def test_pricing_service_calculates_total() -> None:
    settings = SimpleNamespace(water_19l_price=15000, pump_price=45000, empty_bottle_exchange_price=0)
    service = PricingService(settings)  # type: ignore[arg-type]

    assert service.total(ProductType.WATER_19L, 3) == 45000
    assert service.total(ProductType.PUMP, 2) == 90000
    assert service.total(ProductType.EMPTY_BOTTLE_EXCHANGE, 5) == 0


def test_format_stats_uzbek_text() -> None:
    stats = SimpleNamespace(
        today_orders_count=2,
        today_revenue=30000,
        weekly_revenue=120000,
        monthly_revenue=500000,
    )

    text = format_stats(stats)

    assert "Bugungi buyurtmalar soni: <b>2</b>" in text
    assert "Bugungi tushum: <b>30 000 so'm</b>" in text
    assert format_money(500000) == "500 000 so'm"


def test_normalize_database_url_accepts_railway_postgres_scheme() -> None:
    url = normalize_database_url("postgres://user:secret@localhost:5432/marjon")

    assert url == "postgresql+asyncpg://user:secret@localhost:5432/marjon"


def test_normalize_database_url_rejects_bad_values_with_clear_error() -> None:
    try:
        normalize_database_url("not-a-url")
    except DatabaseUrlError as exc:
        assert "DATABASE_URL noto'g'ri formatda" in str(exc)
    else:
        raise AssertionError("DatabaseUrlError expected")
