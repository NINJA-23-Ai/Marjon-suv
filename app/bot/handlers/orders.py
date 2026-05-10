from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import (
    comment_keyboard,
    confirm_keyboard,
    location_keyboard,
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
from app.services.order_service import OrderService
from app.services.pricing import PricingService
from app.services.user_service import UserService
from app.utils.formatting import format_money

router = Router(name="orders")


def clean_choice(text: str | None) -> str:
    return (text or "").replace("💧 ", "").replace("🔁 ", "").replace("💵 ", "").replace("💳 ", "").strip()


@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext, session: AsyncSession, settings: Settings) -> None:
    user = await UserService(session, settings).get_by_telegram_id(message.from_user.id)
    await state.clear()
    await message.answer(
        "❌ Amal bekor qilindi.",
        reply_markup=main_menu(
            message.from_user.id in settings.admin_ids,
            bool(user and (user.is_courier or message.from_user.id in settings.courier_ids)),
        ),
    )


@router.message(F.text == "💧 Buyurtma berish")
async def start_order(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await UserService(session).get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("ℹ️ Avval /start orqali ro'yxatdan o'ting.")
        return
    await state.set_state(OrderState.product)
    await message.answer("💧 <b>Mahsulotni tanlang:</b>", reply_markup=product_keyboard())


@router.message(OrderState.product)
async def choose_product(message: Message, state: FSMContext) -> None:
    try:
        product = ProductType(clean_choice(message.text))
    except ValueError:
        await message.answer("⚠️ Iltimos, ro'yxatdan mahsulot tanlang.", reply_markup=product_keyboard())
        return
    await state.update_data(product=product.value)
    await state.set_state(OrderState.quantity)
    await message.answer("🔢 <b>Miqdorni tanlang</b> yoki raqam kiriting:", reply_markup=quantity_keyboard())


@router.message(OrderState.quantity)
async def choose_quantity(message: Message, state: FSMContext) -> None:
    if not (message.text or "").isdigit():
        await message.answer("⚠️ Miqdor faqat raqam bo'lishi kerak.")
        return
    quantity = int(message.text)
    if quantity < 1 or quantity > 100:
        await message.answer("⚠️ Miqdor 1 dan 100 gacha bo'lishi kerak.")
        return
    await state.update_data(quantity=quantity)
    await state.set_state(OrderState.address)
    await message.answer("🏠 Yetkazib berish <b>manzilini</b> kiriting:")


@router.message(OrderState.address)
async def enter_address(message: Message, state: FSMContext) -> None:
    address = (message.text or "").strip()
    if len(address) < 5:
        await message.answer("⚠️ Manzil kamida 5 ta belgidan iborat bo'lishi kerak.")
        return
    await state.update_data(address=address)
    await state.set_state(OrderState.location)
    await message.answer(
        "📍 Aniqroq yetkazish uchun joylashuvingizni yuboring yoki o'tkazib yuboring:",
        reply_markup=location_keyboard(),
    )


@router.message(OrderState.location)
async def enter_location(message: Message, state: FSMContext) -> None:
    if message.location:
        await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    elif message.text == "⏭ Joylashuvsiz davom etish":
        await state.update_data(latitude=None, longitude=None)
    else:
        await message.answer("⚠️ Joylashuv tugmasini bosing yoki o'tkazib yuboring.", reply_markup=location_keyboard())
        return
    await state.set_state(OrderState.comment)
    await message.answer(
        "💬 Qo'shimcha izoh yozing: masalan, mo'ljal, qavat, domofon.\n"
        "Agar izoh bo'lmasa, o'tkazib yuboring.",
        reply_markup=comment_keyboard(),
    )


@router.message(OrderState.comment)
async def enter_comment(message: Message, state: FSMContext) -> None:
    comment = None if message.text == "⏭ Izohsiz davom etish" else (message.text or "").strip()
    if comment and len(comment) > 1000:
        await message.answer("⚠️ Izoh 1000 belgidan oshmasin.")
        return
    await state.update_data(comment=comment)
    await state.set_state(OrderState.payment_type)
    await message.answer("💳 <b>To'lov turini tanlang:</b>", reply_markup=payment_keyboard())


@router.message(OrderState.payment_type)
async def choose_payment(message: Message, state: FSMContext, settings: Settings) -> None:
    try:
        payment_type = PaymentType(clean_choice(message.text))
    except ValueError:
        await message.answer("⚠️ Iltimos, to'lov turini ro'yxatdan tanlang.", reply_markup=payment_keyboard())
        return
    await state.update_data(payment_type=payment_type.value)
    data = await state.get_data()
    product = ProductType(data["product"])
    total = PricingService(settings).total(product, data["quantity"])
    location = "Yuborilgan" if data.get("latitude") is not None else "Yuborilmagan"
    summary = (
        "🧾 <b>Buyurtmani tasdiqlang:</b>\n\n"
        f"💧 Mahsulot: {product.value}\n"
        f"🔢 Miqdor: {data['quantity']}\n"
        f"🏠 Manzil: {data['address']}\n"
        f"📍 Joylashuv: {location}\n"
        f"💬 Izoh: {data.get('comment') or 'Yo\'q'}\n"
        f"💳 To'lov: {payment_type.value}\n"
        f"💰 Jami: <b>{format_money(total)}</b>"
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
    user = await UserService(session, settings).get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("ℹ️ Avval /start orqali ro'yxatdan o'ting.")
        await state.clear()
        return
    data = await state.get_data()
    order = await OrderService(session, settings).create_order(
        OrderCreate(
            user_id=user.id,
            product=ProductType(data["product"]),
            quantity=data["quantity"],
            address=data["address"],
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            comment=data.get("comment"),
            payment_type=PaymentType(data["payment_type"]),
        )
    )
    await session.commit()
    await NotificationService(bot, settings).notify_new_order(order)
    await state.clear()
    await message.answer(
        "✅ <b>Buyurtmangiz qabul qilindi!</b>\n\nTez orada operator siz bilan bog'lanadi.",
        reply_markup=main_menu(message.from_user.id in settings.admin_ids, user.is_courier),
    )
