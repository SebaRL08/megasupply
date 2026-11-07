from datetime import date

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_report_service
from src.application.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/monthly")
def monthly(year: int | None = Query(None, ge=2000, le=2100), month: int | None = Query(None, ge=1, le=12),
            svc: ReportService = Depends(get_report_service)):
    today = date.today()
    return svc.monthly(year or today.year, month or today.month)

