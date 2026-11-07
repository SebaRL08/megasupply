import os

import qrcode
from PyQt6.QtWidgets import (QFormLayout, QGroupBox, QLineEdit, QPushButton, QSpinBox, QTableWidget,
                             QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import fill_table, info, selected_text, warn


class ProductsTab(QWidget):
    """Alta de productos y generación de su código QR (solo contiene el código)."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.code, self.name, self.desc = QLineEdit(), QLineEdit(), QLineEdit()
        self.code.setPlaceholderText("PROD-004")
        self.minimo = QSpinBox()
        self.minimo.setRange(0, 1000000)
        self.table = QTableWidget()
        btn_add = QPushButton("Crear producto")
        btn_add.clicked.connect(self._create)
        btn_qr = QPushButton("Generar QR del producto seleccionado")
        btn_qr.clicked.connect(self._qr)
        box = QGroupBox("Nuevo producto")
        form = QFormLayout(box)
        form.addRow("Código QR", self.code)
        form.addRow("Nombre", self.name)
        form.addRow("Descripción", self.desc)
        form.addRow("Mínimo en cajón", self.minimo)
        form.addRow(btn_add)
        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self.table)
        layout.addWidget(btn_qr)

    def refresh(self, *_):
        try:
            prods = self.api.get("/api/products/")
        except ApiError as err:
            warn(self, err)
            return
        fill_table(self.table, ["Código", "Nombre", "Descripción", "Mín. cajón"],
                   [[p["codigo_qr"], p["nombre"], p["descripcion"], p["stock_minimo_cajon"]] for p in prods])

    def _create(self, *_):
        body = {"codigo_qr": self.code.text().strip(), "nombre": self.name.text().strip(),
                "descripcion": self.desc.text().strip(), "stock_minimo_cajon": self.minimo.value()}
        try:
            self.api.post("/api/products/", json=body)
        except ApiError as err:
            warn(self, err)
            return
        self.code.clear()
        self.name.clear()
        self.desc.clear()
        self.refresh()

    def _qr(self, *_):
        code = selected_text(self.table, 0)
        if code is None:
            warn(self, "Selecciona un producto de la tabla")
            return
        os.makedirs("qr_generados", exist_ok=True)
        path = os.path.join("qr_generados", f"{code}.png")
        qrcode.make(code).save(path)
        info(self, f"QR guardado en:\n{os.path.abspath(path)}")
