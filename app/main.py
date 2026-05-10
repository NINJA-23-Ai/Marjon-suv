import asyncio
import logging

from app.bot import create_bot, create_dispatcher
from app.config.database import get_engine
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.models import Base

logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    await init_db()
    bot = create_bot(settings)
    dispatcher = create_dispatcher(settings)
    logger.info("Marjon Suv Telegram bot ishga tushdi")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
