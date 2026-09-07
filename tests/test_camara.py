import cv2

# 0 suele ser la cámara por defecto (webcam integrada)
camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("❌ No se pudo abrir la cámara")
else:
    print("✅ Cámara abierta. Presiona 'q' en la ventana de video para salir.")

    while True:
        exito, frame = camara.read()

        if not exito:
            print("❌ No se pudo leer el frame de la cámara")
            break

        cv2.imshow("Prueba de camara - MegaSupply", frame)

        # Espera 1ms por una tecla; si es 'q', rompe el ciclo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()
    