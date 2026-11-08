import pytest

from src.application import ai_report_service as mod
from src.application.ai_report_service import AIReportService

DATA = {"period": "2026-11",
        "most_demanded": [{"codigo_qr": "PROD-001", "nombre": "Tela", "unidades": 90, "salidas": 9}],
        "most_outflow_count": [],
        "near_depletion": [{"codigo_qr": "PROD-003", "cajon": 5, "minimo": 25, "caja": 10}],
        "pending_orders": 1,
        "recommendations": [{"codigo_qr": "PROD-001", "cantidad_sugerida": 90, "nivel_riesgo": "ALTO",
                             "datos_base": "simulado"}]}


class Reports:
    def monthly(self, year, month):
        return DATA


class GoodWriter:
    last_model = "fake-model"

    def __init__(self):
        self.calls = 0

    def write(self, data):
        self.calls += 1
        return "Resumen de la IA"


class BrokenWriter:
    def write(self, data):
        raise RuntimeError("connection lost")


class EmptyWriter:
    def write(self, data):
        return "   "


@pytest.fixture(autouse=True)
def clear_cache():
    mod._CACHE.clear()


def test_ai_summary_is_cached():
    writer = GoodWriter()
    svc = AIReportService(Reports(), writer)
    first = svc.monthly_summary(2026, 11)
    assert (first["source"], first["model"], first["cached"]) == ("ai", "fake-model", False)
    assert svc.monthly_summary(2026, 11)["cached"] is True
    assert writer.calls == 1
    svc.monthly_summary(2026, 11, refresh=True)
    assert writer.calls == 2


@pytest.mark.parametrize("writer", [BrokenWriter(), EmptyWriter(), None])
def test_never_fails_and_falls_back_to_local(writer):
    r = AIReportService(Reports(), writer).monthly_summary(2026, 11)
    assert r["source"] == "local" and "Tela" in r["summary"] and r["note"]


def test_local_fallback_is_not_cached():
    AIReportService(Reports(), BrokenWriter()).monthly_summary(2026, 11)
    assert mod._CACHE == {}
