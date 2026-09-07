from src.db.database import engine, Base
from src.db import models

Base.metadata.create_all(engine)
print("✅ Tablas creadas correctamente")