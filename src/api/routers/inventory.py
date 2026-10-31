from dataclasses import asdict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from src.api.dependencies import get_inventory_service
from src.application.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

class MovementIn(BaseModel):
    codigo_qr: str
    cantidad: int = Field(..., gt=0)

@router.post("/entry", status_code=201)
def entry(body: MovementIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.register_entry(body.codigo_qr, body.cantidad))

@router.post("/exit", status_code=201)
def exit_(body: MovementIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.register_exit(body.codigo_qr, body.cantidad))

@router.get("/stock/{codigo_qr}")
def stock(codigo_qr: str, svc: InventoryService = Depends(get_inventory_service)):
    return {"codigo_qr": codigo_qr, "stock": svc.stock(codigo_qr)}
