from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.admin import (
    admin_order_keyboard,
    courier_order_keyboard,
    courier_select_keyboard,
    order_list_keyboard,
)
from app.bot.keyboards.common import admin_menu_keyboard
from app.bot.states import AdminState
from app.config.settings import Settings
from app.domain.enums import OrderStatus
from app.models.order import Order
from app.services.notification_service import NotificationService
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.utils.formatting import format_customer, format_order, format_stats

router = Router(name="admin")


def is_admin(telegram_id: int, settings: Settings) -> bool:
    return telegram_id in settings.admin_ids


async def is_courier(telegram_id: int, session: AsyncSession, settings: Settings) -> bool:
    user = await UserService(session, settings).get_by_telegram_id(telegram_id)
    return bool(user and user.is_courier)


def admin_keyboard_for_order(order: Order):
    return admin_order_keyboard(
        order.id,
        can_decide=order.status == OrderStatus.NEW,
        can_assign=order.status in {OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.DELIVERING},
    )


@router.message(F.text == "🛠 Admin panel")
async def admin_panel(message: Message, settings: Settings) -> None:
    if not is_admin(message.from_user.id, settings):
        await message.answer("⛔ Bu bo'lim faqat adminlar uchun.")
        return
    await message.answer(
        "🛠 <b>Admin panel</b>\n\nBuyurtmalar, statistika va kuryerlarni boshqaring.",
        reply_markup=admin_menu_keyboard(),
    )


@router.message(F.text == "📊 Statistika")
async def stats(message: Message, session: AsyncSession, settings: Settings) -> None:
    if not is_admin(message.from_user.id, settings):
        await message.answer("⛔ Bu bo'lim faqat adminlar uchun.")
        return
    sales_stats = await OrderService(session, settings).sales_stats()
    await message.answer(format_stats(sales_stats))


@router.message(F.text == "📦 Barcha buyurtmalar")
async def all_orders(message: Message, session: AsyncSession, settings: Settings) -> None:
    if not is_admin(message.from_user.id, settings):
        await message.answer("⛔ Bu bo'lim faqat adminlar uchun.")
        return
    orders = await OrderService(session, settings).list_recent_orders(limit=15)
    await message.answer("📦 <b>Oxirgi buyurtmalar</b>", reply_markup=order_list_keyboard(orders))


@router.message(F.text == "👥 Kuryerlar")
async def couriers(message: Message, session: AsyncSession, settings: Settings) -> None:
    if not is_admin(message.from_user.id, settings):
        await message.answer("⛔ Bu bo'lim faqat adminlar uchun.")
        return
    users = await UserService(session, settings).list_couriers()
    if not users:
        await message.answer("🚚 Hozircha kuryer yo'q. '➕ Kuryer qo\'shish' tugmasidan foydalaning.")
        return
    text = "🚚 <b>Kuryerlar ro'yxati</b>\n\n" + "\n".join(
        f"• {user.name} — <code>{user.telegram_id}</code>" for user in users
    )
    await message.answer(text)


@router.message(F.text == "➕ Kuryer qo'shish")
async def add_courier_start(message: Message, state: FSMContext, settings: Settings) -> None:
    if not is_admin(message.from_user.id, settings):
        await message.answer("⛔ Bu bo'lim faqat adminlar uchun.")
        return
    await state.set_state(AdminState.courier_telegram_id)
    await message.answer(
        "➕ Kuryer qilinadigan foydalanuvchining <b>Telegram ID</b> raqamini yuboring.\n\n"
        "Eslatma: u avval botda /start orqali ro'yxatdan o'tgan bo'lishi kerak."
    )


@router.message(AdminState.courier_telegram_id)
async def add_courier_finish(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if not is_admin(message.from_user.id, settings):
        await state.clear()
        return
    if not (message.text or "").isdigit():
        await message.answer("⚠️ Telegram ID faqat raqam bo'lishi kerak.")
        return
    user = await UserService(session, settings).mark_courier(int(message.text))
    if not user:
        await message.answer("❌ Bunday foydalanuvchi topilmadi. Avval botda ro'yxatdan o'tsin.")
        return
    await session.commit()
    await state.clear()
    await message.answer(f"✅ <b>{user.name}</b> kuryer qilib belgilandi.", reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("admin:"))
async def admin_callbacks(
    callback: CallbackQuery,
    session: AsyncSession,
    settings: Settings,
    bot: Bot,
) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("Bu amal faqat adminlar uchun.", show_alert=True)
        return
    parts = callback.data.split(":")
    action = parts[1]
    order_id = int(parts[2])
    service = OrderService(session, settings)

    if action == "view":
        order = await service.get_order(order_id)
        if not order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return
        await callback.message.edit_text(format_order(order), reply_markup=admin_keyboard_for_order(order))
        await callback.answer()
        return

    if action in {"accept", "cancel"}:
        current_order = await service.get_order(order_id)
        if not current_order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return
        if current_order.status != OrderStatus.NEW:
            await callback.message.edit_text(
                format_order(current_order),
                reply_markup=admin_keyboard_for_order(current_order),
            )
            await callback.answer("Bu buyurtma allaqachon ko'rib chiqilgan", show_alert=True)
            return
        status = OrderStatus.ACCEPTED if action == "accept" else OrderStatus.CANCELED
        order = await service.update_status(order_id, status)
        await session.commit()
        if not order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return
        notification = NotificationService(bot, settings)
        admin_name = callback.from_user.full_name
        if status == OrderStatus.ACCEPTED:
            await notification.notify_order_accepted(order)
            await notification.notify_admin_order_decision(order, accepted=True, admin_name=admin_name)
        else:
            await notification.notify_order_canceled(order)
            await notification.notify_admin_order_decision(order, accepted=False, admin_name=admin_name)
        await callback.message.edit_text(format_order(order), reply_markup=admin_keyboard_for_order(order))
        await callback.answer("Status yangilandi")
        return

    if action == "customer":
        order = await service.get_order(order_id)
        if not order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return
        await callback.message.answer(format_customer(order))
        await callback.answer()
        return

    if action == "assign":
        couriers = await UserService(session, settings).list_couriers()
        if not couriers:
            await callback.answer("Avval kuryer qo'shing", show_alert=True)
            return
        await callback.message.edit_text(
            f"🚚 <b>Buyurtma #{order_id}</b> uchun kuryer tanlang:",
            reply_markup=courier_select_keyboard(order_id, couriers),
        )
        await callback.answer()
        return

    if action == "setcourier":
        courier_id = int(parts[3])
        order = await service.assign_courier(order_id, courier_id)
        await session.commit()
        if not order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return
        notification = NotificationService(bot, settings)
        await notification.notify_courier_assigned(order)
        await notification.notify_admin_courier_assigned(order, admin_name=callback.from_user.full_name)
        await callback.message.edit_text(format_order(order), reply_markup=admin_keyboard_for_order(order))
        await callback.answer("Kuryer tayinlandi")
        return

    await callback.answer("Noma'lum amal", show_alert=True)


@router.message(F.text == "🚚 Mening buyurtmalarim")
async def courier_orders(message: Message, session: AsyncSession, settings: Settings) -> None:
    if not await is_courier(message.from_user.id, session, settings):
        await message.answer("⛔ Bu bo'lim faqat kuryerlar uchun.")
        return
    user = await UserService(session, settings).get_by_telegram_id(message.from_user.id)
    orders = await OrderService(session, settings).list_courier_orders(user.id)
    if not orders:
        await message.answer("🚚 Sizga biriktirilgan faol buyurtma yo'q.")
        return
    for order in orders:
        await message.answer(format_order(order), reply_markup=courier_order_keyboard(order.id))


@router.callback_query(F.data.startswith("courier:"))
async def courier_callbacks(callback: CallbackQuery, session: AsyncSession, settings: Settings, bot: Bot) -> None:
    if not await is_courier(callback.from_user.id, session, settings):
        await callback.answer("Bu amal faqat kuryerlar uchun.", show_alert=True)
        return
    parts = callback.data.split(":")
    action = parts[1]
    order_id = int(parts[2])
    service = OrderService(session, settings)
    order = await service.get_order(order_id)
    user = await UserService(session, settings).get_by_telegram_id(callback.from_user.id)
    if not order or not user or order.courier_id != user.id:
        await callback.answer("Bu buyurtma sizga biriktirilmagan.", show_alert=True)
        return

    if action == "customer":
        await callback.message.answer(format_customer(order))
        await callback.answer()
        return

    if action in {"delivering", "delivered"}:
        status = OrderStatus.DELIVERING if action == "delivering" else OrderStatus.DELIVERED
        order = await service.update_status(order_id, status)
        await session.commit()
        notification = NotificationService(bot, settings)
        if status == OrderStatus.DELIVERING:
            await notification.notify_order_delivering(order)
            reply_markup = courier_order_keyboard(order.id)
        else:
            await notification.notify_order_delivered(order)
            reply_markup = None
        await callback.message.edit_text(format_order(order), reply_markup=reply_markup)
        await callback.answer("Status yangilandi")
        return

    await callback.answer("Noma'lum amal", show_alert=True)
