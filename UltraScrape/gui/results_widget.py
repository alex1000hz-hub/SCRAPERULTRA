"""
UltraScrape - Widget de Visualización de Resultados y Vista Previa en Tiempo Real
"""
from typing import List, Dict, Any, Optional
from core.models import ScrapedItem, ScrapeStats
from exporters.csv_exporter import CsvExporter
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JsonExporter
from exporters.sqlite_exporter import SqliteExporter

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,
        QFileDialog, QMessageBox, QMenu
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QAction
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    class QWidget:
        pass


class ResultsWidget(QWidget):
    def __init__(self, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)

        self.items: List[ScrapedItem] = []
        self.headers: List[str] = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra superior con estadísticas y buscador
        top_bar = QHBoxLayout()

        self.stats_label = QLabel("📊 Encontrados: 0  |  Errores: 0  |  Velocidad: 0 pág/s")
        self.stats_label.setStyleSheet("font-weight: 600; color: #38BDF8;")
        top_bar.addWidget(self.stats_label)

        top_bar.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filtrar en resultados...")
        self.search_input.setMaximumWidth(220)
        self.search_input.textChanged.connect(self.filter_table)
        top_bar.addWidget(self.search_input)

        export_quick_btn = QPushButton("💾 Exportar Rápido")
        export_quick_btn.setObjectName("accentBtn")
        export_quick_btn.clicked.connect(self.quick_export_menu)
        top_bar.addWidget(export_quick_btn)

        clear_btn = QPushButton("🗑️ Limpiar")
        clear_btn.clicked.connect(self.clear_results)
        top_bar.addWidget(clear_btn)

        layout.addLayout(top_bar)

        # Tabla de resultados
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #162032;")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

    def set_headers(self, headers: List[str]):
        """Configura las columnas de la tabla."""
        self.headers = list(headers)
        if "URL Origen" not in self.headers:
            self.headers.append("URL Origen")

        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

    def add_item(self, item: ScrapedItem):
        """Agrega un registro individual en tiempo real."""
        self.items.append(item)

        # Si hay campos nuevos en el item que no están en headers, actualizar
        new_cols = [k for k in item.data.keys() if k not in self.headers and k != "URL Origen"]
        if new_cols:
            all_cols = [h for h in self.headers if h != "URL Origen"] + new_cols + ["URL Origen"]
            self.set_headers(all_cols)

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        for col_idx, header in enumerate(self.headers):
            if header == "URL Origen":
                val = item.source_url
            else:
                val = str(item.data.get(header, ""))

            table_item = QTableWidgetItem(val)
            table_item.setToolTip(val)
            self.table.setItem(row_idx, col_idx, table_item)

        # Auto-scroll si está en las primeras 100 filas
        if row_idx < 100:
            self.table.scrollToBottom()

    def update_stats(self, stats: ScrapeStats):
        self.stats_label.setText(
            f"📊 Encontrados: {stats.records_found}  |  "
            f"Páginas: {stats.pages_scraped}  |  "
            f"Errores: {stats.errors_count}  |  "
            f"Velocidad: {stats.current_speed} pág/s  |  "
            f"Estado: {stats.status_text}"
        )

    def filter_table(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            if not query:
                self.table.setRowHidden(row, False)
                continue

            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def clear_results(self):
        self.items.clear()
        self.table.setRowCount(0)
        self.stats_label.setText("📊 Encontrados: 0  |  Errores: 0  |  Velocidad: 0 pág/s")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = QAction("Copiar Celda", self)
        copy_action.triggered.connect(self.copy_current_cell)
        menu.addAction(copy_action)

        copy_row_action = QAction("Copiar Fila Completa", self)
        copy_row_action.triggered.connect(self.copy_current_row)
        menu.addAction(copy_row_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def copy_current_cell(self):
        item = self.table.currentItem()
        if item:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(item.text())

    def copy_current_row(self):
        row = self.table.currentRow()
        if row >= 0:
            row_data = [self.table.item(row, c).text() if self.table.item(row, c) else "" for c in range(self.table.columnCount())]
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText("\t".join(row_data))

    def quick_export_menu(self):
        if not self.items:
            QMessageBox.information(self, "Sin datos", "No hay registros disponibles para exportar.")
            return

        file_path, filter_selected = QFileDialog.getSaveFileName(
            self,
            "Exportar Resultados",
            "ultrascrape_export.csv",
            "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;SQLite (*.db *.sqlite)"
        )

        if not file_path:
            return

        success = False
        if file_path.endswith(".csv"):
            success = CsvExporter(file_path).export(self.items)
        elif file_path.endswith(".xlsx"):
            success = ExcelExporter(file_path).export(self.items)
        elif file_path.endswith(".json"):
            success = JsonExporter(file_path).export(self.items)
        elif file_path.endswith(".db") or file_path.endswith(".sqlite"):
            success = SqliteExporter(file_path).export(self.items)
        else:
            # Por defecto CSV
            file_path += ".csv"
            success = CsvExporter(file_path).export(self.items)

        if success:
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo exportado correctamente en:\n{file_path}")
        else:
            QMessageBox.critical(self, "Error", "No se pudo completar la exportación.")
