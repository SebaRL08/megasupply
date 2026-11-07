from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.api.dependencies import get_inventory_service
from src.application.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


class EntryIn(BaseModel):
    codigo_qr: str
    cantidad: int = Field(..., gt=0)
    caja: str
    usuario_id: int | None = None


class ExitIn(BaseModel):
    codigo_qr: str
    cantidad: int = Field(..., gt=0)
    cajon: str
    usuario_id: int | None = None


class TransferIn(BaseModel):
    codigo_qr: str
    cantidad: int = Field(..., gt=0)
    caja: str
    cajon: str
    usuario_id: int | None = None


class CajaIn(BaseModel):
    codigo_ubicacion: str = Field(..., min_length=1, max_length=20)
    descripcion: str = ""


class CajonIn(BaseModel):
    codigo_ubicacion: str = Field(..., min_length=1, max_length=20)
    capacidad: int | None = Field(None, gt=0)
    cantidad_minima: int = Field(0, ge=0)


@router.post("/entry", status_code=201)
def entry(b: EntryIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.register_entry(b.codigo_qr, b.cantidad, b.caja, b.usuario_id))


@router.post("/exit", status_code=201)
def exit_(b: ExitIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.register_exit(b.codigo_qr, b.cantidad, b.cajon, b.usuario_id))


@router.post("/transfer", status_code=201)
def transfer(b: TransferIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.transfer(b.codigo_qr, b.cantidad, b.caja, b.cajon, b.usuario_id))


@router.get("/stock/{codigo_qr}")
def stock(codigo_qr: str, svc: InventoryService = Depends(get_inventory_service)):
    return svc.stock(codigo_qr)


@router.get("/snapshot")
def snapshot(svc: InventoryService = Depends(get_inventory_service)):
    return svc.snapshot()


@router.get("/movements")
def movements(limit: int = Query(50, ge=1, le=500), codigo_qr: str | None = None,
              svc: InventoryService = Depends(get_inventory_service)):
    return svc.movements(limit, codigo_qr)


@router.get("/cajas")
def list_cajas(svc: InventoryService = Depends(get_inventory_service)):
    return [asdict(x) for x in svc.cajas()]


@router.get("/cajones")
def list_cajones(svc: InventoryService = Depends(get_inventory_service)):
    return [asdict(x) for x in svc.cajones()]


@router.post("/cajas", status_code=201)
def create_caja(b: CajaIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.add_caja(b.codigo_ubicacion, b.descripcion))


@router.post("/cajones", status_code=201)
def create_cajon(b: CajonIn, svc: InventoryService = Depends(get_inventory_service)):
    return asdict(svc.add_cajon(b.codigo_ubicacion, b.capacidad, b.cantidad_minima))