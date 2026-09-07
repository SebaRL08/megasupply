from sqlalchemy import create_engine, text

# Reemplaza TU_CONTRASEÑA por la que pusiste al instalar PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:TU_CONTRASENA_AQUI@localhost:5432/megasupply"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conexion:
        resultado = conexion.execute(text("SELECT version();"))
        print("✅ Conexión exitosa a PostgreSQL")
        print(resultado.fetchone())
except Exception as error:
    print("❌ Error al conectar:")
    print(error)