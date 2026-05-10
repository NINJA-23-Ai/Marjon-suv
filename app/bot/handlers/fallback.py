from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu
from app.config.settings import Settings
from app.services.user_service import UserService

router = Router(name="fallback")


@router.message()
async def fallback(message: Message, state: FSMContext, session: AsyncSession, settings: Settings) -> None:
    current_state = await state.get_state()
    if current_state:
        await message.answer(
            "🤔 Men bu javobni tushunmadim. Iltimos, ko'rsatilgan tugmalardan foydalaning yoki "
            "amalni bekor qilish uchun <b>❌ Bekor qilish</b> tugmasini bosing."
        )
        return

    user = await UserService(session, settings).get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("👋 Boshlash uchun /start buyrug'ini yuboring.")
        return

    await message.answer(
        "🤖 <b>Marjon Suv bot</b> sizga yordam berishga tayyor.\n\n"
        "Kerakli bo'limni menyudan tanlang:",
        reply_markup=main_menu(
            message.from_user.id in settings.admin_ids,
            user.is_courier or message.from_user.id in settings.courier_ids,
        ),
    )
