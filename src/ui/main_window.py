import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from src.ui.alerts_tab import AlertsTab
from src.ui.api_client import ApiClient
from src.ui.inventory_tab import InventoryTab
from src.ui.orders_tab import OrdersTab
from src.ui.products_tab import ProductsTab
from src.ui.report_tab import ReportTab
from src.ui.scanner_tab import ScannerTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MegaSupply")
        self.resize(1150, 740)
        api = ApiClient()
        self.scanner = ScannerTab(api)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.scanner, "Escáner (Entrada / Salida)")
        for page, title in ((InventoryTab(api), "Inventario y traslados"), (OrdersTab(api), "Pedidos"),
                            (AlertsTab(api), "Alertas y recomendaciones"), (ProductsTab(api), "Productos y QR"),
                            (ReportTab(api), "Informe y mercado")):
            self.tabs.addTab(page, title)
        self.tabs.currentChanged.connect(self._on_tab)
        self.setCentralWidget(self.tabs)

    def _on_tab(self, index: int):
        page = self.tabs.widget(index)
        if hasattr(page, "refresh"):
            page.refresh()

    def closeEvent(self, event):
        self.scanner.stop_camera()
        super().closeEvent(event)


def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
