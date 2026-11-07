import json
from urllib.parse import quote

from PyQt6.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QTableWidget, QTextEdit, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import fill_products, fill_table, selected_text, warn


class AlertsTab(QWidget):
    """Alertas de reabastecimiento y recomendaciones. La IA sugiere; el usuario decide."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.alerts, self.recs = QTableWidget(), QTableWidget()
        self.product = QComboBox()
        self.final = QSpinBox()
        self.final.setRange(0, 1000000)
        self.ai_box = QTextEdit()
        self.ai_box.setReadOnly(True)
        self.ai_box.setMaximumHeight(100)
        btn_gen = QPushButton("Generar recomendación (predicción de demanda)")
        btn_gen.clicked.connect(self._generate)
        btn_ai = QPushButton("Opinión de Gemini (opcional)")
        btn_ai.clicked.connect(self._ask_ai)
        btn_ok, btn_mod, btn_no = QPushButton("Aceptar"), QPushButton("Modificar con esta cantidad:"), QPushButton("Rechazar")
        btn_ok.clicked.connect(lambda *_: self._decide("aceptar"))
        btn_mod.clicked.connect(lambda *_: self._decide("modificar"))
        btn_no.clicked.connect(lambda *_: self._decide("rechazar"))
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.refresh)

        gen = QHBoxLayout()
        gen.addWidget(self.product)
        gen.addWidget(btn_gen)
        gen.addWidget(btn_ai)
        decide = QHBoxLayout()
        for w in (btn_ok, btn_mod, self.final, btn_no):
            decide.addWidget(w)
        box = QGroupBox("Recomendaciones de abastecimiento pendientes")
        inner = QVBoxLayout(box)
        inner.addWidget(QLabel("La IA solo sugiere. Usted revisa y decide: aceptar, modificar o rechazar."))
        inner.addLayout(gen)
        inner.addWidget(self.recs)
        inner.addLayout(decide)
        inner.addWidget(self.ai_box)
        layout = QVBoxLayout(self)
        layout.addWidget(btn_refresh)
        layout.addWidget(QLabel("Alertas: productos por debajo del mínimo en cajones"))
        layout.addWidget(self.alerts, 1)
        layout.addWidget(box, 2)

    def refresh(self, *_):
        try:
            alerts = self.api.get("/api/replenishment/alerts")
            recs = self.api.get("/api/recommendations/", params={"estado": "pendiente"})
            prods = self.api.get("/api/products/")
        except ApiError as err:
            warn(self, err)
            return
        fill_products(self.product, prods)
        fill_table(self.alerts, ["Producto", "Nombre", "En cajón", "Mínimo", "En cajas", "Acción", "Estado"],
                   [[a["codigo_qr"], a["nombre"], a["cajon"], a["minimo"], a["caja"], a["accion"], a["estado"]]
                    for a in alerts])
        fill_table(self.recs, ["ID", "Producto", "Stock", "Demanda 30 d", "Pedidos", "Sugerida", "Riesgo", "Datos base"],
                   [[r["id"], r["codigo_qr"], r["stock_actual"], r["demanda_estimada"], r["pedidos_pendientes"],
                     r["cantidad_sugerida"], r["nivel_riesgo"], r["datos_base"]] for r in recs])

    def _generate(self, *_):
        try:
            self.api.post(f"/api/recommendations/generate/{quote(self.product.currentData(), safe='')}")
        except ApiError as err:
            warn(self, err)
            return
        self.refresh()

    def _decide(self, accion: str):
        rid = selected_text(self.recs, 0)
        if rid is None:
            warn(self, "Selecciona una recomendación de la tabla")
            return
        body = {"accion": accion}
        if accion == "modificar":
            body["cantidad_final"] = self.final.value()
        try:
            self.api.post(f"/api/recommendations/{rid}/decision", json=body)
        except ApiError as err:
            warn(self, err)
            return
        self.refresh()

    def _ask_ai(self, *_):
        try:
            r = self.api.get(f"/api/replenishment/{quote(self.product.currentData(), safe='')}", params={"use_ai": "true"})
        except ApiError as err:
            warn(self, err)
            return
        shown = r.get("ai") or r.get("ai_error") or "Gemini no está configurado (falta GEMINI_API_KEY)."
        self.ai_box.setPlainText(shown if isinstance(shown, str) else json.dumps(shown, ensure_ascii=False, indent=2))
