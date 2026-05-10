from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, name: str, phone: str) -> User:
        user = User(telegram_id=telegram_id, name=name, phone=phone)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(self, telegram_id: int, name: str, phone: str) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.name = name
            user.phone = phone
            await self.session.flush()
            return user
        return await self.create(telegram_id=telegram_id, name=name, phone=phone)
