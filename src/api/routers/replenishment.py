from fastapi import APIRouter, Depends
from src.api.dependencies import get_replenishment_service
from src.application.replenishment_service import ReplenishmentService

router = APIRouter(prefix="/api/replenishment", tags=["Replenishment"])

@router.get("/{codigo_qr}")
def assess(codigo_qr: str, use_ai: bool = False,
           svc: ReplenishmentService = Depends(get_replenishment_service)):
    return svc.assess(codigo_qr, use_ai)
