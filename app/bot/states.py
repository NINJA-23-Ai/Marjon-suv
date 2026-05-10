from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    name = State()
    phone = State()


class OrderState(StatesGroup):
    product = State()
    quantity = State()
    address = State()
    payment_type = State()
    confirm = State()
