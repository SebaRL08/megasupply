import os
os.environ["ZBAR_LOG_LEVEL"] = "0"
import cv2
from pyzbar.pyzbar import decode

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("❌ No se pudo abrir la cámara")
else:
    print("✅ Cámara abierta. Muestra un QR frente a la cámara. Presiona 'q' para salir.")

    ultimo_codigo = None

    while True:
        exito, frame = camara.read()

        if not exito:
            print("❌ No se pudo leer el frame de la cámara")
            break

        codigos_detectados = decode(frame)

        for codigo in codigos_detectados:
            texto = codigo.data.decode("utf-8")

            # Dibuja un rectángulo alrededor del QR detectado
            x, y, w, h = codigo.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if texto != ultimo_codigo:
                print(f"📦 QR detectado: {texto}")
                ultimo_codigo = texto

        cv2.imshow("Lector QR - MegaSupply", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()