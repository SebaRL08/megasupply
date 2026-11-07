from dataclasses import asdict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.dependencies import get_forecast_service
from src.application.forecast_service import ForecastService

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


class DecisionIn(BaseModel):
    accion: str  # aceptar | modificar | rechazar
    cantidad_final: int | None = Field(None, ge=0)


@router.post("/generate/{codigo_qr}", status_code=201)
def generate(codigo_qr: str, svc: ForecastService = Depends(get_forecast_service)):
    return asdict(svc.generate(codigo_qr))


@router.get("/")
def list_recommendations(estado: str | None = None, svc: ForecastService = Depends(get_forecast_service)):
    return [asdict(r) for r in svc.list(estado)]


@router.post("/{rec_id}/decision")
def decide(rec_id: int, b: DecisionIn, svc: ForecastService = Depends(get_forecast_service)):
    return asdict(svc.decide(rec_id, b.accion, b.cantidad_final))
