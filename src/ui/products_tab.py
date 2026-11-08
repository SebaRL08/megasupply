import os

from PyQt6.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QSpinBox,
                             QTableWidget, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import fill_table, info, selected_text, warn
from src.ui.qr_labels import QR_DIR, next_code, save_label


class ProductsTab(QWidget):
    """Alta de productos nuevos y generación de sus etiquetas QR."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.products: list[dict] = []
        self.code, self.name, self.desc = QLineEdit(), QLineEdit(), QLineEdit()
        self.minimo = QSpinBox()
        self.minimo.setRange(0, 1000000)
        self.table = QTableWidget()
        btn_add = QPushButton("Crear producto y generar su QR")
        btn_add.clicked.connect(self._create)
        btn_sel = QPushButton("Regenerar QR del seleccionado")
        btn_sel.clicked.connect(self._qr_selected)
        btn_all = QPushButton("Generar QR de todos los productos")
        btn_all.clicked.connect(self._qr_all)
        btn_open = QPushButton("Abrir carpeta de QR")
        btn_open.clicked.connect(self._open_folder)

        box = QGroupBox("Nuevo producto (el código se sugiere solo, puedes cambiarlo)")
        form = QFormLayout(box)
        form.addRow("Código QR", self.code)
        form.addRow("Nombre", self.name)
        form.addRow("Descripción", self.desc)
        form.addRow("Mínimo en cajón", self.minimo)
        form.addRow(btn_add)
        buttons = QHBoxLayout()
        for b in (btn_sel, btn_all, btn_open):
            buttons.addWidget(b)
        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self.table)
        layout.addLayout(buttons)

    def refresh(self, *_):
        try:
            self.products = self.api.get("/api/products/")
        except ApiError as err:
            warn(self, err)
            return
        fill_table(self.table, ["Código", "Nombre", "Descripción", "Mín. cajón"],
                   [[p["codigo_qr"], p["nombre"], p["descripcion"], p["stock_minimo_cajon"]] for p in self.products])
        if not self.code.text().strip():
            self.code.setText(next_code([p["codigo_qr"] for p in self.products]))

    def _create(self, *_):
        code, name = self.code.text().strip(), self.name.text().strip()
        if not code or not name:
            warn(self, "El código y el nombre son obligatorios")
            return
        body = {"codigo_qr": code, "nombre": name, "descripcion": self.desc.text().strip(),
                "stock_minimo_cajon": self.minimo.value()}
        try:
            self.api.post("/api/products/", json=body)
            path = save_label(code, name)
        except (ApiError, OSError) as err:
            warn(self, err)
            return
        info(self, f"Producto {code} creado.\nEtiqueta QR guardada en:\n{path}")
        self.code.clear()
        self.name.clear()
        self.desc.clear()
        self.refresh()

    def _qr_selected(self, *_):
        code = selected_text(self.table, 0)
        if code is None:
            warn(self, "Selecciona un producto de la tabla")
            return
        try:
            path = save_label(code, selected_text(self.table, 1) or "")
        except OSError as err:
            warn(self, err)
            return
        info(self, f"QR guardado en:\n{path}")

    def _qr_all(self, *_):
        try:
            for p in self.products:
                save_label(p["codigo_qr"], p["nombre"])
        except OSError as err:
            warn(self, err)
            return
        info(self, f"{len(self.products)} etiquetas guardadas en:\n{os.path.abspath(QR_DIR)}")

    def _open_folder(self, *_):
        os.makedirs(QR_DIR, exist_ok=True)
        try:
            os.startfile(os.path.abspath(QR_DIR))  # solo Windows
        except (AttributeError, OSError):
            info(self, f"Carpeta de QR:\n{os.path.abspath(QR_DIR)}")