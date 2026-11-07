import os
from functools import lru_cache

from src.application.forecast_service import ForecastService
from src.application.inventory_service import InventoryService
from src.application.order_service import OrderService
from src.application.product_service import ProductService
from src.application.replenishment_service import ReplenishmentService
from src.application.report_service import ReportService
from src.infrastructure.colombia_open_data import OpenDataClient
from src.infrastructure.forecaster import LinearTrendForecaster
from src.infrastructure.sql_repositories import (SqlInventoryRepository, SqlOrderRepository,
                                                 SqlProductRepository, SqlRecommendationRepository)


@lru_cache
def _products(): return SqlProductRepository()
@lru_cache
def _inventory(): return SqlInventoryRepository()
@lru_cache
def _orders(): return SqlOrderRepository()
@lru_cache
def _recs(): return SqlRecommendationRepository()
@lru_cache
def _open_data(): return OpenDataClient()  # singleton: el circuit breaker conserva su estado


def get_product_service(): return ProductService(_products())
def get_inventory_service(): return InventoryService(_products(), _inventory())
def get_order_service(): return OrderService(_products(), _orders())
def get_open_data(): return _open_data()


def get_replenishment_service():
    advisor = None
    if os.getenv("GEMINI_API_KEY"):
        from src.infrastructure.gemini_advisor import GeminiAdvisor
        advisor = GeminiAdvisor()
    return ReplenishmentService(_products(), _inventory(), _orders(), advisor)


def get_forecast_service():
    return ForecastService(_products(), _inventory(), _orders(), _recs(), LinearTrendForecaster())


def get_report_service():
    return ReportService(_inventory(), get_replenishment_service(), _orders(), _recs())
