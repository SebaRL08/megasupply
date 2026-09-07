import qrcode
import os

# Carpeta donde se guardarán los QR generados
carpeta_salida = "qr_prueba"
os.makedirs(carpeta_salida, exist_ok=True)

# Códigos de producto de prueba
codigos = ["PROD-001", "PROD-002", "PROD-003"]

for codigo in codigos:
    img = qrcode.make(codigo)
    ruta = os.path.join(carpeta_salida, f"{codigo}.png")
    img.save(ruta)
    print(f"✅ Generado: {ruta}")