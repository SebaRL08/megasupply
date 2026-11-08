from datetime import date

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_ai_report_service, get_report_service
from src.application.ai_report_service import AIReportService
from src.application.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _period(year, month):
    today = date.today()
    return year or today.year, month or today.month


@router.get("/monthly")
def monthly(year: int | None = Query(None, ge=2000, le=2100), month: int | None = Query(None, ge=1, le=12),
            svc: ReportService = Depends(get_report_service)):
    return svc.monthly(*_period(year, month))


@router.get("/monthly/ai")
def monthly_ai(year: int | None = Query(None, ge=2000, le=2100), month: int | None = Query(None, ge=1, le=12),
               refresh: bool = False, svc: AIReportService = Depends(get_ai_report_service)):
    """Siempre responde 200 con un resumen: 'source' indica si vino de la IA o de las reglas locales."""
    y, m = _period(year, month)
    return svc.monthly_summary(y, m, refresh)