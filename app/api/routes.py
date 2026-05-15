from fastapi import APIRouter, HTTPException

from app.api.dependencies import SessionDep, SettingsDep
from app.domain.enums import OrderStatus
from app.schemas.order import OrderRead, SalesStats
from app.services.order_service import OrderService

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/admin/stats", response_model=SalesStats)
async def stats(session: SessionDep, settings: SettingsDep) -> SalesStats:
    return await OrderService(session, settings).sales_stats()


@router.patch("/admin/orders/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    session: SessionDep,
    settings: SettingsDep,
) -> OrderRead:
    order = await OrderService(session, settings).update_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    await session.commit()
    return OrderRead.model_validate(order)
