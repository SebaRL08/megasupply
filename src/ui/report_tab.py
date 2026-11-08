import json
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QTextEdit, QVBoxLayout, QWidget)

from src.ui.api_client import ApiClient, ApiError
from src.ui.helpers import warn


def _lines(rows, fmt, empty):
    return [fmt(r) for r in rows] or [empty]


class ReportTab(QWidget):
    """Informe mensual (con y sin IA) y consulta de las APIs colombianas (TRM y GNCV)."""

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api
        self.year, self.month, self.gncv_year = QSpinBox(), QSpinBox(), QSpinBox()
        self.year.setRange(2000, 2100)
        self.year.setValue(date.today().year)
        self.month.setRange(1, 12)
        self.month.setValue(date.today().month)
        self.gncv_year.setRange(2015, 2100)
        self.gncv_year.setValue(2025)
        self.force_ai = QCheckBox("Forzar nueva consulta a la IA")
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        btn_report = QPushButton("Generar informe mensual")
        btn_report.clicked.connect(self._report)
        self.btn_ai = QPushButton("Resumen del mes con IA")
        self.btn_ai.clicked.connect(self._ai_summary)
        btn_trm = QPushButton("Consultar TRM")
        btn_trm.clicked.connect(self._trm)
        btn_gncv = QPushButton("Consultar precios de GNCV")
        btn_gncv.clicked.connect(self._gncv)
        top = QHBoxLayout()
        for w in (QLabel("Año"), self.year, QLabel("Mes"), self.month, btn_report, self.btn_ai, self.force_ai):
            top.addWidget(w)
        market = QHBoxLayout()
        for w in (btn_trm, QLabel("Año GNCV"), self.gncv_year, btn_gncv):
            market.addWidget(w)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(market)
        layout.addWidget(self.out)

    def _report(self, *_):
        try:
            r = self.api.get("/api/reports/monthly", params={"year": self.year.value(), "month": self.month.value()})
        except ApiError as err:
            warn(self, err)
            return
        text = [f"INFORME MENSUAL {r['period']}", "", "Productos con mayor demanda (unidades):"]
        text += _lines(r["most_demanded"], lambda x: f"  {x['codigo_qr']} {x['nombre']}: {x['unidades']} u", "  Sin salidas en el mes")
        text += ["", "Productos con más salidas:"]
        text += _lines(r["most_outflow_count"], lambda x: f"  {x['codigo_qr']}: {x['salidas']} salidas", "  Sin salidas en el mes")
        text += ["", "Próximos a agotarse (cajón bajo el mínimo):"]
        text += _lines(r["near_depletion"], lambda x: f"  {x['codigo_qr']}: {x['cajon']}/{x['minimo']} → {x['accion']}", "  Ninguno")
        text += ["", f"Pedidos pendientes: {r['pending_orders']}", "", "Recomendaciones pendientes de decisión:"]
        text += _lines(r["recommendations"],
                       lambda x: f"  {x['codigo_qr']}: sugerido {x['cantidad_sugerida']} (riesgo {x['nivel_riesgo']}, datos {x['datos_base']})",
                       "  Ninguna")
        self.out.setPlainText("\n".join(text))

    def _ai_summary(self, *_):
        self.out.setPlainText("Generando resumen con IA... (puede tardar hasta 30 segundos)")
        self.btn_ai.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()
        try:
            r = self.api.get("/api/reports/monthly/ai", timeout=45.0,
                             params={"year": self.year.value(), "month": self.month.value(),
                                     "refresh": "true" if self.force_ai.isChecked() else "false"})
        except ApiError as err:
            warn(self, err)
            return
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_ai.setEnabled(True)
        origin = f"IA ({r['model']})" if r["source"] == "ai" else "reglas locales"
        if r["cached"]:
            origin += ", respuesta guardada"
        note = f"\n\nNota: {r['note']}" if r["note"] else ""
        self.out.setPlainText(f"RESUMEN DEL MES {r['period']}: {origin}\n\n{r['summary']}{note}")

    def _show(self, path, params=None):
        try:
            self.out.setPlainText(json.dumps(self.api.get(path, params=params), ensure_ascii=False, indent=2))
        except ApiError as err:
            warn(self, err)

    def _trm(self, *_):
        self._show("/api/market/trm")

    def _gncv(self, *_):
        self._show("/api/market/gncv", {"year": str(self.gncv_year.value())})
        