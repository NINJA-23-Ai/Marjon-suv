from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import admin, fallback, orders, start
from app.config.settings import Settings
from app.middlewares.db import DatabaseSessionMiddleware


def create_dispatcher(settings: Settings) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(DatabaseSessionMiddleware())
    dispatcher["settings"] = settings
    dispatcher.include_router(start.router)
    dispatcher.include_router(admin.router)
    dispatcher.include_router(orders.router)
    dispatcher.include_router(fallback.router)
    return dispatcher


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
