import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_URL = f"postgresql+psycopg2://postgres:{DB_PASSWORD}@localhost:5432/megasupply"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conexion:
        resultado = conexion.execute(text("SELECT version();"))
        print("✅ Conexión exitosa a PostgreSQL")
        print(resultado.fetchone())
except Exception as error:
    print("❌ Error al conectar:")
    print(error)