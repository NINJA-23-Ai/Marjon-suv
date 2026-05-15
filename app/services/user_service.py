from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.users = UserRepository(session)
        self.settings = settings

    async def register(self, data: UserCreate):
        return await self.users.get_or_create(
            telegram_id=data.telegram_id,
            name=data.name.strip(),
            phone=data.phone.strip(),
        )

    async def get_by_telegram_id(self, telegram_id: int):
        return await self.users.get_by_telegram_id(telegram_id)

    async def mark_courier(self, telegram_id: int):
        return await self.users.mark_courier(telegram_id)

    async def list_couriers(self):
        return await self.users.list_couriers()
