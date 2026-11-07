from datetime import date, timedelta

import pytest

from src.application.forecast_service import ForecastService
from src.application.inventory_service import InventoryService
from src.application.order_service import OrderService
from src.application.product_service import ProductService
from src.domain.entities import InvalidOperation
from src.infrastructure.forecaster import LinearTrendForecaster


class FixedForecaster:
    def predict(self, history, horizon_days):
        return 100.0


def test_forecaster_constant_demand():
    today = date.today()
    history = [(today - timedelta(days=i), 10) for i in range(19, -1, -1)]
    assert abs(LinearTrendForecaster().predict(history, 30) - 300) < 1


def test_forecaster_edge_cases():
    f = LinearTrendForecaster()
    assert f.predict([], 30) == 0.0
    assert f.predict([(date.today(), 6)], 30) == 180


def test_recommendation_combines_ml_and_business_rules(repos):
    p, i, o, r = repos["products"], repos["inventory"], repos["orders"], repos["recs"]
    ProductService(p).create("PROD-001", "Tela", "", 10)
    inv = InventoryService(p, i)
    inv.add_caja("A-01")
    inv.register_entry("PROD-001", 40, "A-01")
    OrderService(p, o).create("PROD-001", 20, None)
    svc = ForecastService(p, i, o, r, FixedForecaster())
    rec = svc.generate("PROD-001")
    # 100 (demanda) + 20 (pedidos) + 10 (mínimo) - 40 (stock) = 90
    assert (rec.cantidad_sugerida, rec.nivel_riesgo, rec.datos_base) == (90, "ALTO", "real")
    done = svc.decide(rec.id, "modificar", 80)
    assert (done.estado, done.cantidad_final) == ("modificada", 80)
    with pytest.raises(InvalidOperation):
        svc.decide(rec.id, "aceptar")
