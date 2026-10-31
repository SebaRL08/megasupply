from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_open_data
from src.infrastructure.colombia_open_data import OpenDataClient
from src.infrastructure.resilient_http import ExternalAPIError, CircuitOpenError
from src.infrastructure.analytics import trm_stats, gncv_stats

router = APIRouter(prefix="/api/market", tags=["Colombian Open Data"])


@router.get("/trm")
def trm(limit: int = Query(90, ge=7, le=365), client: OpenDataClient = Depends(get_open_data)):
    try:
        rows = client.trm_history(limit)
    except CircuitOpenError as e:
        raise HTTPException(503, str(e))
    except ExternalAPIError as e:
        raise HTTPException(502, str(e))
    return {"source": "datos.gov.co/32sa-8pi3", "latest": rows[0] if rows else None,
            "stats": trm_stats(rows) if rows else None}


@router.get("/gncv")
def gncv(year: str = Query("2025", pattern=r"^\d{4}$"),
         client: OpenDataClient = Depends(get_open_data)):
    try:
        rows = client.gncv_prices(year)
    except CircuitOpenError as e:
        raise HTTPException(503, str(e))
    except ExternalAPIError as e:
        raise HTTPException(502, str(e))
    return {"source": "datos.gov.co/he3q-86dn", "year": year,
            "stats": gncv_stats(rows) if rows else None}
