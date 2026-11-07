import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import models  # noqa: F401
from src.db.database import Base
from src.infrastructure.sql_repositories import (SqlInventoryRepository, SqlOrderRepository,
                                                 SqlProductRepository, SqlRecommendationRepository)


@pytest.fixture
def repos():
    """Repositorios reales sobre SQLite en memoria: prueban el SQL sin tocar PostgreSQL."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sf = sessionmaker(bind=engine)
    return {"products": SqlProductRepository(sf), "inventory": SqlInventoryRepository(sf),
            "orders": SqlOrderRepository(sf), "recs": SqlRecommendationRepository(sf)}
