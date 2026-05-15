from typing import Protocol

from app.domain.enums import ProductType


class PriceSettings(Protocol):
    water_19l_price: int
    pump_price: int
    empty_bottle_exchange_price: int


class PricingService:
    def __init__(self, settings: PriceSettings) -> None:
        self.settings = settings

    def unit_price(self, product: ProductType) -> int:
        prices = {
            ProductType.WATER_19L: self.settings.water_19l_price,
            ProductType.PUMP: self.settings.pump_price,
            ProductType.EMPTY_BOTTLE_EXCHANGE: self.settings.empty_bottle_exchange_price,
        }
        return prices[product]

    def total(self, product: ProductType, quantity: int) -> int:
        if quantity < 1:
            raise ValueError("Miqdor kamida 1 bo'lishi kerak")
        return self.unit_price(product) * quantity
