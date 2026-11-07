"""Escáner: cámara + QR + ENTRADA (suma a caja) o SALIDA (resta de cajón)."""
import time
from urllib.parse import quote

import cv2
from pyzbar.pyzbar import decode
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError


class ScannerTab(QWidget):
    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.cap = None
        self.mode = "entrada"
        self.product = None
        self.last_code, self.last_ts, self.frames = None, 0.0, 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._build()
        self._set_mode("entrada")

    def _build(self):
        self.video = QLabel("Cámara detenida")
        self.video.setFixedSize(640, 480)
        self.video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video.setStyleSheet("background:#222;color:#ccc")
        self.btn_cam = QPushButton("Iniciar cámara")
        self.btn_cam.clicked.connect(self._toggle_camera)

        self.btn_in = QPushButton("ENTRADA (suma a una caja)")
        self.btn_out = QPushButton("SALIDA (resta de un cajón)")
        for b in (self.btn_in, self.btn_out):
            b.setCheckable(True)
            b.setMinimumHeight(52)
        self.btn_in.setStyleSheet("QPushButton:checked{background:#2e7d32;color:white;font-weight:bold}")
        self.btn_out.setStyleSheet("QPushButton:checked{background:#c62828;color:white;font-weight:bold}")
        self.btn_in.clicked.connect(lambda *_: self._set_mode("entrada"))
        self.btn_out.clicked.connect(lambda *_: self._set_mode("salida"))

        self.manual = QLineEdit()
        self.manual.setPlaceholderText("Código manual (ej. PROD-001)")
        btn_manual = QPushButton("Buscar")
        btn_manual.clicked.connect(self._manual_search)
        self.info = QLabel("Escanea un QR para identificar el producto")
        self.info.setWordWrap(True)
        self.loc_label = QLabel()
        self.location = QComboBox()
        self.qty = QSpinBox()
        self.qty.setRange(1, 100000)
        self.auto_one = QCheckBox("Registrar 1 unidad automáticamente al escanear")
        self.btn_confirm = QPushButton("Confirmar movimiento")
        self.btn_confirm.setMinimumHeight(44)
        self.btn_confirm.clicked.connect(self._confirm)
        self.status = QLabel("")
        self.status.setWordWrap(True)

        left = QVBoxLayout()
        left.addWidget(self.video)
        left.addWidget(self.btn_cam)
        left.addStretch()
        modes = QHBoxLayout()
        modes.addWidget(self.btn_in)
        modes.addWidget(self.btn_out)
        manual = QHBoxLayout()
        manual.addWidget(self.manual)
        manual.addWidget(btn_manual)
        right = QVBoxLayout()
        for item in (modes, manual):
            right.addLayout(item)
        for w in (self.info, self.loc_label, self.location, QLabel("Cantidad:"), self.qty,
                  self.auto_one, self.btn_confirm, self.status):
            right.addWidget(w)
        right.addStretch()
        root = QHBoxLayout(self)
        root.addLayout(left)
        root.addLayout(right, 1)

    def _status(self, text: str, ok: bool = True):
        self.status.setText(text)
        self.status.setStyleSheet("color:#2e7d32" if ok else "color:#c62828")

    def refresh(self):
        self._set_mode(self.mode)

    def _set_mode(self, mode: str):
        self.mode = mode
        self.btn_in.setChecked(mode == "entrada")
        self.btn_out.setChecked(mode == "salida")
        self.loc_label.setText("Caja destino:" if mode == "entrada" else "Cajón de origen:")
        try:
            items = self.api.get("/api/inventory/cajas" if mode == "entrada" else "/api/inventory/cajones")
        except ApiError as err:
            self._status(str(err), ok=False)
            items = []
        self.location.clear()
        self.location.addItems([i["codigo"] for i in items])

    def _toggle_camera(self, *_):
        if self.cap is not None:
            self.stop_camera()
            return
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self._status("No se pudo abrir la cámara. Usa el código manual.", ok=False)
            return
        self.cap = cap
        self.btn_cam.setText("Detener cámara")
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.btn_cam.setText("Iniciar cámara")
        self.video.clear()
        self.video.setText("Cámara detenida")

    def _tick(self):
        if self.cap is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            self._status("No se pudo leer la cámara", ok=False)
            return
        self.frames += 1
        if self.frames % 3 == 0:
            for code in decode(frame):
                x, y, w, h = code.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                self._on_code(code.data.decode("utf-8", errors="ignore").strip())
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
        self.video.setPixmap(QPixmap.fromImage(img).scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio))

    def _manual_search(self, *_):
        code = self.manual.text().strip()
        if code:
            self._on_code(code, force=True)

    def _on_code(self, text: str, force: bool = False):
        now = time.monotonic()
        if not force and text == self.last_code and now - self.last_ts < 2.5:
            return
        self.last_code, self.last_ts = text, now
        try:
            self.product = self.api.get(f"/api/products/code/{quote(text, safe='')}")
            self._render_info()
        except ApiError as err:
            self.product = None
            self.info.setText(f"QR leído: {text}\n{err}")
            self._status("Producto no encontrado", ok=False)
            return
        if self.auto_one.isChecked() and not force:
            self._register(1)

    def _render_info(self):
        p = self.product
        s = self.api.get(f"/api/inventory/stock/{quote(p['codigo_qr'], safe='')}")
        self.info.setText(f"{p['nombre']} ({p['codigo_qr']})\nEn cajas: {s['caja']}  |  En cajones: {s['cajon']}  |  "
                          f"Total: {s['total']}\nMínimo en cajón: {s['minimo']}")

    def _confirm(self, *_):
        self._register(self.qty.value())

    def _register(self, qty: int):
        if not self.product:
            self._status("Primero escanea un producto", ok=False)
            return
        loc = self.location.currentText()
        if not loc:
            self._status("No hay ubicaciones registradas", ok=False)
            return
        entry = self.mode == "entrada"
        body = {"codigo_qr": self.product["codigo_qr"], "cantidad": qty, ("caja" if entry else "cajon"): loc}
        try:
            self.api.post("/api/inventory/entry" if entry else "/api/inventory/exit", json=body)
            self._render_info()
        except ApiError as err:
            self._status(f"❌ {err}", ok=False)
            return
        self._status(f"✅ {self.mode.upper()}: {qty} x {self.product['nombre']} en {loc}")

    