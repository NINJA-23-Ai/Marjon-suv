from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    name = State()
    phone = State()


class OrderState(StatesGroup):
    product = State()
    quantity = State()
    address = State()
    location = State()
    comment = State()
    payment_type = State()
    confirm = State()


class AdminState(StatesGroup):
    courier_telegram_id = State()
