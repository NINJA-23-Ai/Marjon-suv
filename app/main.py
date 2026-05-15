import asyncio
import logging

from app.bot import create_bot, create_dispatcher
from app.config.database import get_engine
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.config.schema import init_schema

logger = logging.getLogger(__name__)


async def init_db() -> None:
    await init_schema(get_engine())


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    await init_db()
    bot = create_bot(settings)
    dispatcher = create_dispatcher(settings)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Marjon Suv Telegram bot ishga tushdi")
    await dispatcher.start_polling(
        bot,
        allowed_updates=dispatcher.resolve_used_update_types(),
        close_bot_session=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
