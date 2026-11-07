from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers import (ai_assistant, inventory, market, orders, products,
                             recommendations, replenishment, reports)
from src.domain import entities as ent

app = FastAPI(title="MegaSupply API", version="3.0.0",
              description="Hexagonal modular monolith: inventory, QR, forecasting and Colombian open data.")

for r in (products, inventory, orders, replenishment, recommendations, reports, market, ai_assistant):
    app.include_router(r.router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}


ERRORS = {ent.ProductNotFound: 404, ent.LocationNotFound: 404, ent.OrderNotFound: 404,
          ent.RecommendationNotFound: 404, ent.DuplicateProduct: 409, ent.InsufficientStock: 409,
          ent.ProductInUse: 409, ent.InvalidOperation: 400}


def _handler(code):
    async def handler(request: Request, exc: Exception):
        return JSONResponse(status_code=code, content={"detail": str(exc)})
    return handler


for exc_type, code in ERRORS.items():
    app.add_exception_handler(exc_type, _handler(code))
    