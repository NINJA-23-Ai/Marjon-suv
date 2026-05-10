from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, telegram_id: int, name: str, phone: str, is_courier: bool = False) -> User:
        user = User(telegram_id=telegram_id, name=name, phone=phone, is_courier=is_courier)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(self, telegram_id: int, name: str, phone: str, is_courier: bool = False) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.name = name
            user.phone = phone
            user.is_courier = user.is_courier or is_courier
            await self.session.flush()
            return user
        return await self.create(telegram_id=telegram_id, name=name, phone=phone, is_courier=is_courier)

    async def mark_courier(self, telegram_id: int) -> User | None:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return None
        user.is_courier = True
        await self.session.flush()
        return user

    async def list_couriers(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.is_courier.is_(True)).order_by(User.name)
        )
        return list(result.scalars().all())
