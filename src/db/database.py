# Inicio de modelado de base de datos
import os # -> Interacción con el sistema operativo para obtener variables de entorno
from dotenv import load_dotenv # -> Carga de variables de entorno para el archivo .env
from sqlalchemy import create_engine # -> Creación de la conexión a la base de datos
from sqlalchemy.orm import sessionmaker, declarative_base # -> Creación de sesiones y base para los modelos

# Abrimos el archivo .env y cargamos las variables de entorno
load_dotenv()

# Creamos la "URL" para poder conectar la db
DB_PASSWORD = os.getenv("DB_PASSWORD") # -> Contraseña guardada en .env 
DATABASE_URL = f"postgresql+psycopg2://postgres:{DB_PASSWORD}@localhost:5432/megasupply"

engine = create_engine(DATABASE_URL) # -> Motor de conexión a la base de datos
# Motor es el que nos permite conectarnos a la base de datos y ejecutar consultas SQL

SessionLocal = sessionmaker(bind=engine) # -> Creamos una sesion para interactuar con db

Base = declarative_base() # -> Creamos la base para los modelos de la base de datos
# Asi creamos tablas y heredar este modelo en los modelos de la base de datos