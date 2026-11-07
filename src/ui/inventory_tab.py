from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QTableWidget, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import fill_products, fill_table, info, warn


class InventoryTab(QWidget):
    """Inventario por ubicación, traslado caja -> cajón e historial de movimientos."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.table, self.moves = QTableWidget(), QTableWidget()
        self.product, self.caja, self.cajon = QComboBox(), QComboBox(), QComboBox()
        self.qty = QSpinBox()
        self.qty.setRange(1, 100000)
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.refresh)
        btn_transfer = QPushButton("Trasladar caja → cajón")
        btn_transfer.clicked.connect(self._transfer)

        box = QGroupBox("Traslado de caja a cajón")
        row = QHBoxLayout(box)
        for label, w in (("Producto", self.product), ("Caja", self.caja), ("Cajón", self.cajon), ("Cantidad", self.qty)):
            row.addWidget(QLabel(label))
            row.addWidget(w)
        row.addWidget(btn_transfer)

        layout = QVBoxLayout(self)
        layout.addWidget(btn_refresh)
        layout.addWidget(QLabel("Inventario (en rojo: cajón por debajo del mínimo)"))
        layout.addWidget(self.table, 2)
        layout.addWidget(box)
        layout.addWidget(QLabel("Últimos movimientos"))
        layout.addWidget(self.moves, 2)

    def refresh(self, *_):
        try:
            snap = self.api.get("/api/inventory/snapshot")
            moves = self.api.get("/api/inventory/movements", params={"limit": 30})
            cajas = self.api.get("/api/inventory/cajas")
            cajones = self.api.get("/api/inventory/cajones")
            prods = self.api.get("/api/products/")
        except ApiError as err:
            warn(self, err)
            return
        fill_table(self.table, ["Código", "Producto", "Cajas", "Cajones", "Total", "Mín. cajón", "Ubicaciones"],
                   [[s["codigo_qr"], s["nombre"], s["caja"], s["cajon"], s["total"], s["minimo"], s["ubicaciones"]]
                    for s in snap])
        for r, s in enumerate(snap):
            if s["cajon"] < s["minimo"]:
                for c in range(self.table.columnCount()):
                    self.table.item(r, c).setBackground(QColor("#ffcdd2"))
        fill_table(self.moves, ["Fecha", "Tipo", "Producto", "Cantidad", "Origen", "Destino", "Datos"],
                   [[m["fecha_hora"].replace("T", " ")[:19], m["tipo"], m["codigo_qr"], m["cantidad"], m["origen"],
                     m["destino"], "simulado" if m["es_simulado"] else "real"] for m in moves])
        fill_products(self.product, prods)
        self.caja.clear()
        self.caja.addItems([c["codigo"] for c in cajas])
        self.cajon.clear()
        self.cajon.addItems([c["codigo"] for c in cajones])

    def _transfer(self, *_):
        body = {"codigo_qr": self.product.currentData(), "cantidad": self.qty.value(),
                "caja": self.caja.currentText(), "cajon": self.cajon.currentText()}
        try:
            self.api.post("/api/inventory/transfer", json=body)
        except ApiError as err:
            warn(self, err)
            return
        info(self, "Traslado registrado")
        self.refresh()

