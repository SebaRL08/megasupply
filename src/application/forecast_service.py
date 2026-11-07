import math
from datetime import datetime, timedelta

from src.domain.entities import InvalidOperation, ProductNotFound, Recommendation, RecommendationNotFound
from src.domain.ports import (DemandForecaster, InventoryRepository, OrderRepository,
                              ProductRepository, RecommendationRepository)

ACTIONS = {"aceptar": "aceptada", "modificar": "modificada", "rechazar": "rechazada"}


class ForecastService:
    """Parte ML: forecaster.predict. Parte negocio: stock, pedidos, mínimo y cantidad sugerida."""

    def __init__(self, products: ProductRepository, inventory: InventoryRepository,
                 orders: OrderRepository, recommendations: RecommendationRepository,
                 forecaster: DemandForecaster, history_days: int = 90, horizon_days: int = 30):
        self._products = products
        self._inventory = inventory
        self._orders = orders
        self._recs = recommendations
        self._forecaster = forecaster
        self._history_days = history_days
        self._horizon = horizon_days

    def generate(self, codigo_qr: str) -> Recommendation:
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        since = datetime.now() - timedelta(days=self._history_days)
        history = self._inventory.daily_outflows(p.id, since)
        demanda = self._forecaster.predict(history, self._horizon)  # Machine Learning
        caja, cajon = self._inventory.totals(p.id)
        stock = caja + cajon
        pendientes = self._orders.pending_quantity(p.id)
        # Lógica de negocio tradicional
        sugerida = max(0, math.ceil(demanda + pendientes + p.stock_minimo_cajon - stock))
        base = demanda + pendientes
        ratio = stock / base if base > 0 else 99
        riesgo = "ALTO" if ratio < 0.5 else "MEDIO" if ratio < 1 else "BAJO"
        datos = "simulado" if self._inventory.has_simulated_data(p.id) else "real"
        return self._recs.add(Recommendation(p.id, datetime.now(), stock, round(demanda), pendientes,
                                             sugerida, riesgo, datos))

    def list(self, estado: str | None = None) -> list[Recommendation]:
        return self._recs.list(estado)

    def decide(self, rec_id: int, accion: str, cantidad_final: int | None = None) -> Recommendation:
        if accion not in ACTIONS:
            raise InvalidOperation(f"Action must be one of {sorted(ACTIONS)}")
        rec = self._recs.get(rec_id)
        if rec is None:
            raise RecommendationNotFound(f"Recommendation {rec_id} not found")
        if rec.estado != "pendiente":
            raise InvalidOperation("This recommendation was already decided")
        if accion == "aceptar":
            final = rec.cantidad_sugerida
        elif accion == "modificar":
            if cantidad_final is None or cantidad_final < 0:
                raise InvalidOperation("A final quantity >= 0 is required to modify")
            final = cantidad_final
        else:
            final = None
        return self._recs.decide(rec_id, ACTIONS[accion], final)
    