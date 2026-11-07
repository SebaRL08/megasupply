from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox, QTableWidget, QTableWidgetItem


def fill_table(table: QTableWidget, headers: list[str], rows: list[list]):
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


def selected_text(table: QTableWidget, col: int = 0):
    row = table.currentRow()
    if row < 0:
        return None
    item = table.item(row, col)
    return item.text() if item else None


def fill_products(combo, products: list[dict]):
    combo.clear()
    for p in products:
        combo.addItem(f"{p['codigo_qr']} - {p['nombre']}", p["codigo_qr"])


def warn(parent, message):
    QMessageBox.warning(parent, "MegaSupply", str(message))


def info(parent, message):
    QMessageBox.information(parent, "MegaSupply", str(message))

    