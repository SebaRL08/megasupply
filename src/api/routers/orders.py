from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.dependencies import get_order_service
from src.application.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["Orders"])


class OrderIn(BaseModel):
    codigo_qr: str
    cantidad_solicitada: int = Field(..., gt=0)
    fecha_esperada: date | None = None


class StateIn(BaseModel):
    estado: str


@router.post("/", status_code=201)
def create_order(b: OrderIn, svc: OrderService = Depends(get_order_service)):
    return asdict(svc.create(b.codigo_qr, b.cantidad_solicitada, b.fecha_esperada))


@router.get("/")
def list_orders(estado: str | None = None, svc: OrderService = Depends(get_order_service)):
    return [asdict(o) for o in svc.list(estado)]


@router.put("/{order_id}/state")
def set_state(order_id: int, b: StateIn, svc: OrderService = Depends(get_order_service)):
    return asdict(svc.set_state(order_id, b.estado))
