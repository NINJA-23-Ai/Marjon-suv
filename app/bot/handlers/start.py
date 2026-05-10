from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import contact_keyboard, main_menu
from app.bot.states import RegistrationState
from app.config.settings import Settings
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = Router(name="start")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession, settings: Settings) -> None:
    user = await UserService(session).get_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"Assalomu alaykum, {user.name}! Marjon Suv botiga xush kelibsiz.",
            reply_markup=main_menu(message.from_user.id in settings.admin_ids),
        )
        return
    await state.set_state(RegistrationState.name)
    await message.answer("Assalomu alaykum! Iltimos, ismingizni kiriting:")


@router.message(RegistrationState.name)
async def registration_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Ism kamida 2 ta belgidan iborat bo'lishi kerak. Qayta kiriting:")
        return
    await state.update_data(name=name)
    await state.set_state(RegistrationState.phone)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=contact_keyboard())


@router.message(RegistrationState.phone)
async def registration_phone(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    settings: Settings,
) -> None:
    phone = message.contact.phone_number if message.contact else (message.text or "").strip()
    normalized_phone = phone.replace(" ", "").replace("-", "")
    if not normalized_phone.startswith("+") and normalized_phone.isdigit():
        normalized_phone = "+" + normalized_phone
    if not normalized_phone.startswith("+") or not normalized_phone[1:].isdigit():
        await message.answer("Telefon raqam formati noto'g'ri. Masalan: +998901234567")
        return
    data = await state.get_data()
    user = await UserService(session).register(
        UserCreate(telegram_id=message.from_user.id, name=data["name"], phone=normalized_phone)
    )
    await state.clear()
    await message.answer(
        f"Rahmat, {user.name}! Endi buyurtma berishingiz mumkin.",
        reply_markup=main_menu(message.from_user.id in settings.admin_ids),
    )
