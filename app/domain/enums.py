from enum import StrEnum


class ProductType(StrEnum):
    WATER_19L = "19L suv"
    PUMP = "Pompa"
    EMPTY_BOTTLE_EXCHANGE = "Bo'sh idish almashtirish"


class PaymentType(StrEnum):
    CASH = "Naqd"
    CARD_TRANSFER = "Bank kartasiga o'tkazma"


class OrderStatus(StrEnum):
    NEW = "NEW"
    ACCEPTED = "ACCEPTED"
    DELIVERING = "DELIVERING"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
