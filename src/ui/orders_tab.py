from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QTableWidget, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import fill_products, fill_table, selected_text, warn


class OrdersTab(QWidget):
    """Pedidos próximos: insumo para el análisis de abastecimiento."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.product = QComboBox()
        self.qty = QSpinBox()
        self.qty.setRange(1, 1000000)
        self.date = QDateEdit(QDate.currentDate().addDays(7))
        self.date.setCalendarPopup(True)
        self.table = QTableWidget()
        btn_add = QPushButton("Crear pedido")
        btn_add.clicked.connect(self._create)
        btn_done = QPushButton("Marcar seleccionado como completado")
        btn_done.clicked.connect(self._complete)
        form = QHBoxLayout()
        for label, w in (("Producto", self.product), ("Cantidad", self.qty), ("Fecha esperada", self.date)):
            form.addWidget(QLabel(label))
            form.addWidget(w)
        form.addWidget(btn_add)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.table)
        layout.addWidget(btn_done)

    def refresh(self, *_):
        try:
            prods = self.api.get("/api/products/")
            orders = self.api.get("/api/orders/")
        except ApiError as err:
            warn(self, err)
            return
        fill_products(self.product, prods)
        fill_table(self.table, ["ID", "Producto", "Cantidad", "Fecha esperada", "Estado"],
                   [[o["id"], o["codigo_qr"], o["cantidad_solicitada"], o["fecha_esperada"], o["estado"]]
                    for o in orders])

    def _create(self, *_):
        body = {"codigo_qr": self.product.currentData(), "cantidad_solicitada": self.qty.value(),
                "fecha_esperada": self.date.date().toPyDate().isoformat()}
        try:
            self.api.post("/api/orders/", json=body)
        except ApiError as err:
            warn(self, err)
            return
        self.refresh()

    def _complete(self, *_):
        oid = selected_text(self.table, 0)
        if oid is None:
            warn(self, "Selecciona un pedido de la tabla")
            return
        try:
            self.api.put(f"/api/orders/{oid}/state", json={"estado": "completado"})
        except ApiError as err:
            warn(self, err)
            return
        self.refresh()
