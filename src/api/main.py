from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.routers import products, inventory, replenishment, market, ai_assistant
from src.domain.entities import ProductNotFound, DuplicateProduct, InsufficientStock

app = FastAPI(title="MegaSupply API", version="2.0.0",
              description="Hexagonal modular monolith: FastAPI, PostgreSQL, Gemini and Colombian open data.")

for r in (products, inventory, replenishment, market, ai_assistant):
    app.include_router(r.router)

def _handler(status_code):
    async def h(request: Request, exc: Exception):
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})
    return h

app.add_exception_handler(ProductNotFound, _handler(404))
app.add_exception_handler(DuplicateProduct, _handler(409))
app.add_exception_handler(InsufficientStock, _handler(409))
