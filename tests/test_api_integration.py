from fastapi.testclient import TestClient
from src.api.main import app
from src.api import dependencies as dep
from src.application.product_service import ProductService
from src.application.inventory_service import InventoryService
from src.infrastructure.memory_repositories import InMemoryProductRepository, InMemoryMovementRepository

def make_client():
    pr, mr = InMemoryProductRepository(), InMemoryMovementRepository()
    app.dependency_overrides[dep.get_product_service] = lambda: ProductService(pr)
    app.dependency_overrides[dep.get_inventory_service] = lambda: InventoryService(pr, mr)
    return TestClient(app)

P = {"codigo_qr": "PROD-001", "nombre": "Tela", "descripcion": "x", "stock_minimo_cajon": 5}

def test_create_and_get_product():
    c = make_client()
    r = c.post("/api/products/", json=P)
    assert r.statuss_code == 201
    assert c.get(f"/api/products/{r.json()['id']}").json()["codigo_qr"] == "PROD-001"

def test_not_found():
    assert make_client().get("/api/products/9999").status_code == 404

def test_validation_error():
    assert make_client().post("/api/products/", json={**P, "stock_minimo_cajon": -1}).status_code == 422

def test_exit_without_stock_is_rejected():
    c = make_client()
    c.post("/api/products/", json=P)
    assert c.post("/api/inventory/exit", json={"codigo_qr": "PROD-001", "cantidad": 1}).status_code == 409

def test_entry_then_exit_updates_stock():
    c = make_client()
    c.post("/api/products/", json=P)
    c.post("/api/inventory/entry", json={"codigo_qr": "PROD-001", "cantidad": 10})
    c.post("/api/inventory/exit", json={"codigo_qr": "PROD-001", "cantidad": 4})
    assert c.get("/api/inventory/stock/PROD-001").json()["stock"] == 6
