from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def register(self, data: UserCreate):
        return await self.users.get_or_create(
            telegram_id=data.telegram_id,
            name=data.name.strip(),
            phone=data.phone.strip(),
        )

    async def get_by_telegram_id(self, telegram_id: int):
        return await self.users.get_by_telegram_id(telegram_id)
