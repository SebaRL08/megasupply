import pytest

from src.application.inventory_service import InventoryService
from src.application.product_service import ProductService
from src.domain.entities import InsufficientStock, InvalidOperation, LocationNotFound


@pytest.fixture
def inv(repos):
    ProductService(repos["products"]).create("PROD-001", "Tela", "", 10)
    svc = InventoryService(repos["products"], repos["inventory"])
    svc.add_caja("A-01")
    svc.add_cajon("C-01", 100, 0)
    return svc


def test_entry_goes_to_box(inv):
    inv.register_entry("PROD-001", 50, "A-01")
    s = inv.stock("PROD-001")
    assert (s["caja"], s["cajon"], s["total"]) == (50, 0, 50)


def test_transfer_moves_between_zones(inv):
    inv.register_entry("PROD-001", 100, "A-01")
    inv.transfer("PROD-001", 20, "A-01", "C-01")
    s = inv.stock("PROD-001")
    assert (s["caja"], s["cajon"], s["total"]) == (80, 20, 100)


def test_exit_requires_stock_in_drawer(inv):
    inv.register_entry("PROD-001", 50, "A-01")
    with pytest.raises(InsufficientStock):
        inv.register_exit("PROD-001", 5, "C-01")


def test_exit_after_transfer_and_never_exceeds(inv):
    inv.register_entry("PROD-001", 30, "A-01")
    inv.transfer("PROD-001", 30, "A-01", "C-01")
    inv.register_exit("PROD-001", 10, "C-01")
    assert inv.stock("PROD-001")["cajon"] == 20
    with pytest.raises(InsufficientStock):
        inv.register_exit("PROD-001", 21, "C-01")


def test_failed_operation_changes_nothing(inv):
    inv.register_entry("PROD-001", 10, "A-01")
    with pytest.raises(InsufficientStock):
        inv.transfer("PROD-001", 50, "A-01", "C-01")
    assert inv.stock("PROD-001")["caja"] == 10


def test_unknown_location_and_invalid_quantity(inv):
    with pytest.raises(LocationNotFound):
        inv.register_entry("PROD-001", 5, "Z-99")
    with pytest.raises(InvalidOperation):
        inv.register_entry("PROD-001", 0, "A-01")


def test_transfer_respects_drawer_capacity(inv):
    inv.register_entry("PROD-001", 500, "A-01")
    with pytest.raises(InvalidOperation):
        inv.transfer("PROD-001", 101, "A-01", "C-01")


def test_movements_are_logged(inv):
    inv.register_entry("PROD-001", 10, "A-01")
    inv.transfer("PROD-001", 4, "A-01", "C-01")
    assert [m["tipo"] for m in inv.movements()] == ["traslado", "entrada"]