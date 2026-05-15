from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models import Base


async def init_schema(engine: AsyncEngine) -> None:
    """Create MVP tables and add safe columns needed by newer bot flows."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_courier BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS comment TEXT"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS courier_id INTEGER REFERENCES users(id)"))
        await conn.execute(
            text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()")
        )
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_is_courier ON users (is_courier)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_courier_id ON orders (courier_id)"))
