from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import (
    confirm_keyboard,
    main_menu,
    payment_keyboard,
    product_keyboard,
    quantity_keyboard,
)
from app.bot.states import OrderState
from app.config.settings import Settings
from app.domain.enums import PaymentType, ProductType
from app.schemas.order import OrderCreate
from app.services.notification_service import NotificationService
from app.utils.formatting import format_money
from app.services.order_service import OrderService
from app.services.pricing import PricingService
from app.services.user_service import UserService

router = Router(name="orders")


@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext, settings: Settings) -> None:
    await state.clear()
    await message.answer(
        "Amal bekor qilindi.", reply_markup=main_menu(message.from_user.id in settings.admin_ids)
    )


@router.message(F.text == "💧 Buyurtma berish")
async def start_order(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await UserService(session).get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        return
    await state.set_state(OrderState.product)
    await message.answer("Mahsulotni tanlang:", reply_markup=product_keyboard())


@router.message(OrderState.product)
async def choose_product(message: Message, state: FSMContext) -> None:
    try:
        product = ProductType(message.text)
    except ValueError:
        await message.answer("Iltimos, ro'yxatdan mahsulot tanlang.", reply_markup=product_keyboard())
        return
    await state.update_data(product=product.value)
    await state.set_state(OrderState.quantity)
    await message.answer("Miqdorni tanlang yoki raqam kiriting:", reply_markup=quantity_keyboard())


@router.message(OrderState.quantity)
async def choose_quantity(message: Message, state: FSMContext) -> None:
    if not (message.text or "").isdigit():
        await message.answer("Miqdor faqat raqam bo'lishi kerak.")
        return
    quantity = int(message.text)
    if quantity < 1 or quantity > 100:
        await message.answer("Miqdor 1 dan 100 gacha bo'lishi kerak.")
        return
    await state.update_data(quantity=quantity)
    await state.set_state(OrderState.address)
    await message.answer("Yetkazib berish manzilini kiriting:")


@router.message(OrderState.address)
async def enter_address(message: Message, state: FSMContext) -> None:
    address = (message.text or "").strip()
    if len(address) < 5:
        await message.answer("Manzil kamida 5 ta belgidan iborat bo'lishi kerak.")
        return
    await state.update_data(address=address)
    await state.set_state(OrderState.payment_type)
    await message.answer("To'lov turini tanlang:", reply_markup=payment_keyboard())


@router.message(OrderState.payment_type)
async def choose_payment(message: Message, state: FSMContext, settings: Settings) -> None:
    try:
        payment_type = PaymentType(message.text)
    except ValueError:
        await message.answer("Iltimos, to'lov turini ro'yxatdan tanlang.", reply_markup=payment_keyboard())
        return
    await state.update_data(payment_type=payment_type.value)
    data = await state.get_data()
    product = ProductType(data["product"])
    total = PricingService(settings).total(product, data["quantity"])
    summary = (
        "Buyurtmani tasdiqlang:\n\n"
        f"Mahsulot: {product.value}\n"
        f"Miqdor: {data['quantity']}\n"
        f"Manzil: {data['address']}\n"
        f"To'lov: {payment_type.value}\n"
        f"Jami: {format_money(total)}"
    )
    await state.set_state(OrderState.confirm)
    await message.answer(summary, reply_markup=confirm_keyboard())


@router.message(OrderState.confirm, F.text == "✅ Tasdiqlash")
async def confirm_order(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
    bot: Bot,
) -> None:
    user = await UserService(session).get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        await state.clear()
        return
    data = await state.get_data()
    order = await OrderService(session, settings).create_order(
        OrderCreate(
            user_id=user.id,
            product=ProductType(data["product"]),
            quantity=data["quantity"],
            address=data["address"],
            payment_type=PaymentType(data["payment_type"]),
        )
    )
    await session.commit()
    await NotificationService(bot, settings).notify_new_order(order)
    await state.clear()
    await message.answer(
        "Buyurtmangiz qabul qilindi! Tez orada operator siz bilan bog'lanadi.",
        reply_markup=main_menu(message.from_user.id in settings.admin_ids),
    )
