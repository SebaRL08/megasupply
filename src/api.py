from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

app = FastAPI(
    title="MegaSupply API - Session 9 & 10",
    version="1.0.0",
    description="Backend inventory management system with FastAPI and Google Gemini integration."
)

# Registrar tus routers aquí...
from src.routers import products, ai_assistant
app.include_router(products.router)
app.include_router(ai_assistant.router)