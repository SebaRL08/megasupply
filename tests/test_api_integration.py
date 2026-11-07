import pytest
from fastapi.testclient import TestClient

from src.api import dependencies as dep
from src.api.main import app
from src.application.forecast_service import ForecastService
from src.application.inventory_service import InventoryService
from src.application.order_service import OrderService
from src.application.product_service import ProductService
from src.application.replenishment_service import ReplenishmentService

P = {"codigo_qr": "PROD-001", "nombre": "Tela", "descripcion": "x", "stock_minimo_cajon": 10}


class FixedForecaster:
    def predict(self, history, horizon_days):
        return 100.0


@pytest.fixture
def client(repos):
    p, i, o, r = repos["products"], repos["inventory"], repos["orders"], repos["recs"]
    app.dependency_overrides[dep.get_product_service] = lambda: ProductService(p)
    app.dependency_overrides[dep.get_inventory_service] = lambda: InventoryService(p, i)
    app.dependency_overrides[dep.get_order_service] = lambda: OrderService(p, o)
    app.dependency_overrides[dep.get_replenishment_service] = lambda: ReplenishmentService(p, i, o, None)
    app.dependency_overrides[dep.get_forecast_service] = lambda: ForecastService(p, i, o, r, FixedForecaster())
    yield TestClient(app)
    app.dependency_overrides.clear()


def setup_stock(c, entry=100, to_drawer=0):
    c.post("/api/products/", json=P)
    c.post("/api/inventory/cajas", json={"codigo_ubicacion": "A-01"})
    c.post("/api/inventory/cajones", json={"codigo_ubicacion": "C-01", "capacidad": 200})
    c.post("/api/inventory/entry", json={"codigo_qr": "PROD-001", "cantidad": entry, "caja": "A-01"})
    if to_drawer:
        c.post("/api/inventory/transfer", json={"codigo_qr": "PROD-001", "cantidad": to_drawer,
                                                "caja": "A-01", "cajon": "C-01"})


def test_health_and_product_crud(client):
    assert client.get("/health").json() == {"status": "ok"}
    r = client.post("/api/products/", json=P)
    assert r.status_code == 201
    assert client.get("/api/products/code/PROD-001").json()["id"] == r.json()["id"]
    assert client.post("/api/products/", json=P).status_code == 409


def test_not_found_and_validation(client):
    assert client.get("/api/products/9999").status_code == 404
    assert client.post("/api/products/", json={**P, "stock_minimo_cajon": -1}).status_code == 422


def test_full_flow_entry_transfer_exit(client):
    setup_stock(client, 100, 20)
    s = client.get("/api/inventory/stock/PROD-001").json()
    assert (s["caja"], s["cajon"]) == (80, 20)
    assert client.post("/api/inventory/exit", json={"codigo_qr": "PROD-001", "cantidad": 5, "cajon": "C-01"}).status_code == 201
    assert client.post("/api/inventory/exit", json={"codigo_qr": "PROD-001", "cantidad": 500, "cajon": "C-01"}).status_code == 409


def test_alerts_when_drawer_below_minimum(client):
    setup_stock(client, 100, 5)
    alerts = client.get("/api/replenishment/alerts").json()
    assert alerts[0]["codigo_qr"] == "PROD-001" and alerts[0]["faltante"] == 5


def test_orders_and_recommendation_flow(client):
    setup_stock(client, 40, 0)
    o = client.post("/api/orders/", json={"codigo_qr": "PROD-001", "cantidad_solicitada": 20})
    assert o.status_code == 201
    rec = client.post("/api/recommendations/generate/PROD-001").json()
    assert rec["cantidad_sugerida"] == 90 and rec["nivel_riesgo"] == "ALTO"
    d = client.post(f"/api/recommendations/{rec['id']}/decision", json={"accion": "aceptar"})
    assert d.json()["estado"] == "aceptada"
    assert client.put(f"/api/orders/{o.json()['id']}/state", json={"estado": "completado"}).json()["estado"] == "completado"