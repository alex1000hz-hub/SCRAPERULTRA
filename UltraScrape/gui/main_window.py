"""
UltraScrape - Ventana Principal de la Aplicación (PySide6)
"""
import os
import sys
from typing import List, Optional
from core.models import (
    ProjectConfig, SelectorConfig, DynamicConfig,
    PaginationConfig, ProcessorConfig, ScrapingSettings, ExportConfig, ScrapeStats
)
from gui.styles import DARK_THEME_QSS
from gui.worker import ScraperWorker
from gui.selector_dialog import SelectorDialog
from gui.results_widget import ResultsWidget
from gui.project_manager import ProjectManager, ProjectDialog

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QTextEdit, QPushButton, QCheckBox, QComboBox,
        QSpinBox, QDoubleSpinBox, QTabWidget, QGroupBox, QTableWidget,
        QTableWidgetItem, QHeaderView, QProgressBar, QFileDialog,
        QMessageBox, QSplitter, QStatusBar, QDialog, QFormLayout
    )
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon, QFont
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    class QMainWindow:
        pass


class MainWindow(QMainWindow):
    def __init__(self, projects_dir: str = "projects", parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)

        self.setWindowTitle("UltraScrape Studio - Web Scraping Suite Profesional")
        self.resize(1280, 850)
        self.setStyleSheet(DARK_THEME_QSS)

        self.project_manager = ProjectManager(projects_dir)
        self.current_project = ProjectConfig(name="Nuevo_Proyecto")
        self.worker: Optional[ScraperWorker] = None

        self.init_ui()
        self.load_project_to_ui(self.current_project)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # 1. Barra Superior / Header de Proyecto
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_label = QLabel("⚡ ULTRASCRAPE STUDIO")
        title_label.setObjectName("titleLabel")
        subtitle = QLabel("Visual Web Scraper & Dynamic Crawler Engine")
        subtitle.setObjectName("subtitleLabel")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.proj_name_input = QLineEdit()
        self.proj_name_input.setPlaceholderText("Nombre del Proyecto")
        self.proj_name_input.setMaximumWidth(180)
        header_layout.addWidget(self.proj_name_input)

        new_proj_btn = QPushButton("📄 Nuevo")
        new_proj_btn.clicked.connect(self.new_project)
        header_layout.addWidget(new_proj_btn)

        open_proj_btn = QPushButton("📂 Abrir")
        open_proj_btn.clicked.connect(self.open_project_dialog)
        header_layout.addWidget(open_proj_btn)

        save_proj_btn = QPushButton("💾 Guardar")
        save_proj_btn.setObjectName("accentBtn")
        save_proj_btn.clicked.connect(self.save_project)
        header_layout.addWidget(save_proj_btn)

        main_layout.addLayout(header_layout)

        # 2. Splitter Principal: Panel Izquierdo (Configuración) / Panel Derecho (Resultados y Logs)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        # ----------------- PANEL IZQUIERDO: CONFIGURACIÓN -----------------
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        # Pestañas de Configuración
        config_tabs = QTabWidget()
        left_layout.addWidget(config_tabs)

        # TAB 1: Entrada y Selectores
        tab_main = QWidget()
        tab_main_layout = QVBoxLayout(tab_main)
        tab_main_layout.setSpacing(10)

        # Grupo: Entrada del Sitio
        site_group = QGroupBox("🌐 1. Entrada del Sitio (URLs)")
        site_layout = QVBoxLayout(site_group)

        url_input_box = QHBoxLayout()
        self.start_url_input = QLineEdit()
        self.start_url_input.setPlaceholderText("https://ejemplo.com/productos")
        url_input_box.addWidget(self.start_url_input)

        load_file_btn = QPushButton("📁 Cargar TXT/CSV")
        load_file_btn.clicked.connect(self.load_urls_from_file)
        url_input_box.addWidget(load_file_btn)
        site_layout.addLayout(url_input_box)

        # Múltiples URLs
        self.multi_url_edit = QTextEdit()
        self.multi_url_edit.setPlaceholderText("O introduce múltiples URLs (una por línea)...")
        self.multi_url_edit.setMaximumHeight(65)
        site_layout.addWidget(self.multi_url_edit)

        headers_btn = QPushButton("⚙️ Headers & Cookies de Sesión")
        headers_btn.clicked.connect(self.open_headers_dialog)
        site_layout.addWidget(headers_btn)

        tab_main_layout.addWidget(site_group)

        # Grupo: Selectores
        sel_group = QGroupBox("🔎 2. Qué Datos Extraer (Selectores)")
        sel_layout = QVBoxLayout(sel_group)

        container_box = QHBoxLayout()
        container_box.addWidget(QLabel("Contenedor (ej. .product-card):"))
        self.container_input = QLineEdit()
        self.container_input.setPlaceholderText("Opcional: selector de tarjeta/fila")
        container_box.addWidget(self.container_input)
        sel_layout.addLayout(container_box)

        # Tabla de selectores
        self.selector_table = QTableWidget()
        self.selector_table.setColumnCount(4)
        self.selector_table.setHorizontalHeaderLabels(["Campo", "Selector", "Tipo", "Atributo"])
        self.selector_table.horizontalHeader().setStretchLastSection(True)
        self.selector_table.setSelectionBehavior(QTableWidget.SelectRows)
        sel_layout.addWidget(self.selector_table)

        sel_btn_box = QHBoxLayout()
        add_sel_btn = QPushButton("➕ Agregar Selector")
        add_sel_btn.setObjectName("accentBtn")
        add_sel_btn.clicked.connect(self.add_selector)
        sel_btn_box.addWidget(add_sel_btn)

        edit_sel_btn = QPushButton("✏️ Editar")
        edit_sel_btn.clicked.connect(self.edit_selector)
        sel_btn_box.addWidget(edit_sel_btn)

        del_sel_btn = QPushButton("🗑️ Eliminar")
        del_sel_btn.clicked.connect(self.delete_selector)
        sel_btn_box.addWidget(del_sel_btn)
        sel_layout.addLayout(sel_btn_box)

        tab_main_layout.addWidget(sel_group)
        config_tabs.addTab(tab_main, "🎯 Extracción")

        # TAB 2: Scraping Dinámico y Paginación
        tab_dyn = QWidget()
        tab_dyn_layout = QVBoxLayout(tab_dyn)
        tab_dyn_layout.setSpacing(12)

        # Grupo Dinámico Playwright
        dyn_group = QGroupBox("⚙️ 3. Scraping Dinámico (Playwright / JavaScript)")
        dyn_layout = QVBoxLayout(dyn_group)

        self.js_check = QCheckBox("Habilitar JavaScript y navegador dinámico")
        dyn_layout.addWidget(self.js_check)

        self.headless_check = QCheckBox("Modo Headless (ocultar ventana del navegador)")
        self.headless_check.setChecked(True)
        dyn_layout.addWidget(self.headless_check)

        self.scroll_check = QCheckBox("Scroll infinito automático")
        dyn_layout.addWidget(self.scroll_check)

        scroll_opt_box = QHBoxLayout()
        scroll_opt_box.addWidget(QLabel("Límite de scrolls:"))
        self.max_scrolls_spin = QSpinBox()
        self.max_scrolls_spin.setValue(5)
        self.max_scrolls_spin.setRange(1, 100)
        scroll_opt_box.addWidget(self.max_scrolls_spin)

        scroll_opt_box.addWidget(QLabel("Espera (s):"))
        self.scroll_delay_spin = QDoubleSpinBox()
        self.scroll_delay_spin.setValue(1.0)
        self.scroll_delay_spin.setRange(0.2, 10.0)
        scroll_opt_box.addWidget(self.scroll_delay_spin)
        dyn_layout.addLayout(scroll_opt_box)

        load_more_box = QHBoxLayout()
        load_more_box.addWidget(QLabel("Botón 'Load More':"))
        self.load_more_input = QLineEdit()
        self.load_more_input.setPlaceholderText("Selector CSS del botón")
        load_more_box.addWidget(self.load_more_input)
        dyn_layout.addLayout(load_more_box)

        wait_box = QHBoxLayout()
        wait_box.addWidget(QLabel("Esperar selector:"))
        self.wait_sel_input = QLineEdit()
        self.wait_sel_input.setPlaceholderText("ej. .content-loaded")
        wait_box.addWidget(self.wait_sel_input)
        dyn_layout.addLayout(wait_box)

        tab_dyn_layout.addWidget(dyn_group)

        # Grupo Paginación
        pag_group = QGroupBox("📄 Paginación Automática")
        pag_layout = QVBoxLayout(pag_group)

        self.pag_enable_check = QCheckBox("Habilitar paginación")
        pag_layout.addWidget(self.pag_enable_check)

        pag_type_box = QHBoxLayout()
        pag_type_box.addWidget(QLabel("Tipo de paginación:"))
        self.pag_type_combo = QComboBox()
        self.pag_type_combo.addItems(["Botón Siguiente (Next Button)", "Patrón de URL (?page={page})"])
        pag_type_box.addWidget(self.pag_type_combo)
        pag_layout.addLayout(pag_type_box)

        next_btn_box = QHBoxLayout()
        next_btn_box.addWidget(QLabel("Selector Siguiente:"))
        self.next_sel_input = QLineEdit()
        self.next_sel_input.setPlaceholderText("ej. a.next, li.pagination-next a")
        next_btn_box.addWidget(self.next_sel_input)
        pag_layout.addLayout(next_btn_box)

        pattern_box = QHBoxLayout()
        pattern_box.addWidget(QLabel("Plantilla URL:"))
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("ej. https://ejemplo.com/tienda?page={page}")
        pattern_box.addWidget(self.pattern_input)
        pag_layout.addLayout(pattern_box)

        max_page_box = QHBoxLayout()
        max_page_box.addWidget(QLabel("Máximo de páginas:"))
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setValue(5)
        self.max_pages_spin.setRange(1, 1000)
        max_page_box.addWidget(self.max_pages_spin)
        pag_layout.addLayout(max_page_box)

        tab_dyn_layout.addWidget(pag_group)
        tab_dyn_layout.addStretch()
        config_tabs.addTab(tab_dyn, "⚡ Dinámico & Páginas")

        # TAB 3: Procesamiento y Control
        tab_proc = QWidget()
        tab_proc_layout = QVBoxLayout(tab_proc)
        tab_proc_layout.setSpacing(12)

        proc_group = QGroupBox("🧹 4. Procesamiento y Limpieza de Datos")
        proc_layout = QVBoxLayout(proc_group)

        self.dedup_check = QCheckBox("Eliminar registros duplicados")
        self.dedup_check.setChecked(True)
        proc_layout.addWidget(self.dedup_check)

        self.trim_check = QCheckBox("Limpiar espacios en blanco y saltos de línea")
        self.trim_check.setChecked(True)
        proc_layout.addWidget(self.trim_check)

        self.price_norm_check = QCheckBox("Normalizar precios a formato numérico")
        self.price_norm_check.setChecked(True)
        proc_layout.addWidget(self.price_norm_check)

        self.date_norm_check = QCheckBox("Convertir fechas (relativas y formatos varios a ISO)")
        proc_layout.addWidget(self.date_norm_check)

        self.url_val_check = QCheckBox("Validar URLs y convertir rutas relativas a absolutas")
        self.url_val_check.setChecked(True)
        proc_layout.addWidget(self.url_val_check)

        self.drop_incomp_check = QCheckBox("Eliminar registros incompletos o vacíos")
        proc_layout.addWidget(self.drop_incomp_check)

        tab_proc_layout.addWidget(proc_group)

        # Control del scraping
        ctrl_group = QGroupBox("🚀 7. Control de Velocidad y Red")
        ctrl_layout = QFormLayout(ctrl_group)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setValue(1.0)
        self.delay_spin.setRange(0.0, 60.0)
        self.delay_spin.setSuffix(" seg")
        ctrl_layout.addRow("Delay entre solicitudes:", self.delay_spin)

        self.max_records_spin = QSpinBox()
        self.max_records_spin.setValue(1000)
        self.max_records_spin.setRange(0, 1000000)
        self.max_records_spin.setSpecialValueText("Sin límite (0)")
        ctrl_layout.addRow("Límite de registros:", self.max_records_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setValue(20)
        self.timeout_spin.setRange(5, 120)
        self.timeout_spin.setSuffix(" seg")
        ctrl_layout.addRow("Timeout por petición:", self.timeout_spin)

        self.retries_spin = QSpinBox()
        self.retries_spin.setValue(3)
        self.retries_spin.setRange(0, 10)
        ctrl_layout.addRow("Reintentos por error:", self.retries_spin)

        tab_proc_layout.addWidget(ctrl_group)
        tab_proc_layout.addStretch()
        config_tabs.addTab(tab_proc, "🧹 Limpieza & Red")

        # TAB 4: Exportación
        tab_export = QWidget()
        tab_exp_layout = QVBoxLayout(tab_export)

        exp_group = QGroupBox("📦 5. Formato de Exportación")
        exp_form = QFormLayout(exp_group)

        self.exp_format_combo = QComboBox()
        self.exp_format_combo.addItems(["CSV (*.csv)", "Excel (*.xlsx)", "JSON (*.json)", "SQLite (*.db)"])
        exp_form.addRow("Formato de Salida:", self.exp_format_combo)

        out_box = QHBoxLayout()
        self.exp_path_input = QLineEdit()
        self.exp_path_input.setPlaceholderText("Ruta automática en carpeta results/ del proyecto")
        out_box.addWidget(self.exp_path_input)

        browse_out_btn = QPushButton("📁 Examinar...")
        browse_out_btn.clicked.connect(self.browse_export_path)
        out_box.addWidget(browse_out_btn)
        exp_form.addRow("Archivo Destino:", out_box)

        tab_exp_layout.addWidget(exp_group)
        tab_exp_layout.addStretch()
        config_tabs.addTab(tab_export, "📦 Exportación")

        # Barra de Acción Inferior Izquierda (Iniciar / Pausar / Detener)
        action_bar = QHBoxLayout()
        self.start_btn = QPushButton("▶ INICIAR")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_scraping)
        action_bar.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸️ PAUSAR")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        action_bar.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("🛑 DETENER")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scraping)
        action_bar.addWidget(self.stop_btn)

        left_layout.addLayout(action_bar)
        splitter.addWidget(left_container)

        # ----------------- PANEL DERECHO: VISTA PREVIA Y LOGS -----------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(10)

        # Pestañas de Resultados
        results_tabs = QTabWidget()
        right_layout.addWidget(results_tabs, 1)

        # Pestaña 1: Vista Previa de Datos
        self.results_widget = ResultsWidget()
        results_tabs.addTab(self.results_widget, "📊 Vista Previa de Datos")

        # Pestaña 2: Consola de Logs en Vivo
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #0B1120; font-family: 'Consolas', monospace; font-size: 12px;")
        results_tabs.addTab(self.log_console, "📋 Consola de Eventos")

        # Barra de progreso inferior derecha
        progress_box = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Listo para iniciar")
        progress_box.addWidget(self.progress_bar)

        self.status_label = QLabel("Estado: En espera")
        self.status_label.setStyleSheet("color: #64748B;")
        progress_box.addWidget(self.status_label)

        right_layout.addLayout(progress_box)
        splitter.addWidget(right_container)

        splitter.setSizes([460, 800])

    def log(self, msg: str):
        self.log_console.append(msg)
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def add_selector(self):
        url = self.start_url_input.text().strip()
        dlg = SelectorDialog(test_url=url, parent=self)
        if dlg.exec():
            cfg = dlg.get_config()
            self.current_project.selectors.append(cfg)
            self.refresh_selectors_table()

    def edit_selector(self):
        row = self.selector_table.currentRow()
        if row < 0 or row >= len(self.current_project.selectors):
            QMessageBox.warning(self, "Aviso", "Selecciona un selector para editar.")
            return

        cfg = self.current_project.selectors[row]
        url = self.start_url_input.text().strip()
        dlg = SelectorDialog(selector_config=cfg, test_url=url, parent=self)
        if dlg.exec():
            self.current_project.selectors[row] = dlg.get_config()
            self.refresh_selectors_table()

    def delete_selector(self):
        row = self.selector_table.currentRow()
        if row < 0 or row >= len(self.current_project.selectors):
            return
        del self.current_project.selectors[row]
        self.refresh_selectors_table()

    def refresh_selectors_table(self):
        self.selector_table.setRowCount(len(self.current_project.selectors))
        headers = []
        for r, s in enumerate(self.current_project.selectors):
            self.selector_table.setItem(r, 0, QTableWidgetItem(s.name))
            self.selector_table.setItem(r, 1, QTableWidgetItem(s.selector))
            self.selector_table.setItem(r, 2, QTableWidgetItem(s.selector_type.upper()))
            self.selector_table.setItem(r, 3, QTableWidgetItem(s.attribute))
            headers.append(s.name)
        self.results_widget.set_headers(headers)

    def load_urls_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Cargar lista de URLs", "", "Archivos de texto (*.txt *.csv)")
        if not file_path:
            return

        urls = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and line.startswith("http"):
                    urls.append(line)

        if urls:
            self.start_url_input.setText(urls[0])
            self.multi_url_edit.setText("\n".join(urls))
            QMessageBox.information(self, "URLs cargadas", f"Se cargaron {len(urls)} URLs correctamente.")

    def open_headers_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Headers y Cookies Personalizadas")
        dlg.resize(450, 350)
        v = QVBoxLayout(dlg)

        v.addWidget(QLabel("User-Agent:"))
        ua_edit = QLineEdit(self.current_project.settings.user_agent)
        v.addWidget(ua_edit)

        v.addWidget(QLabel("Headers Adicionales (Formato: Clave: Valor por línea):"))
        h_edit = QTextEdit()
        h_text = "\n".join(f"{k}: {val}" for k, val in self.current_project.settings.headers.items())
        h_edit.setText(h_text)
        v.addWidget(h_edit)

        v.addWidget(QLabel("Cookies (Formato: nombre=valor; nombre2=valor2):"))
        c_edit = QLineEdit()
        c_text = "; ".join(f"{k}={val}" for k, val in self.current_project.settings.cookies.items())
        c_edit.setText(c_text)
        v.addWidget(c_edit)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("startBtn")
        save_btn.clicked.connect(dlg.accept)
        btn_box.addWidget(save_btn)
        v.addLayout(btn_box)

        if dlg.exec():
            self.current_project.settings.user_agent = ua_edit.text().strip()
            # Parse headers
            new_headers = {}
            for line in h_edit.toPlainText().splitlines():
                if ":" in line:
                    k, val = line.split(":", 1)
                    new_headers[k.strip()] = val.strip()
            self.current_project.settings.headers = new_headers

            # Parse cookies
            new_cookies = {}
            for chunk in c_edit.text().split(";"):
                if "=" in chunk:
                    k, val = chunk.split("=", 1)
                    new_cookies[k.strip()] = val.strip()
            self.current_project.settings.cookies = new_cookies

    def browse_export_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Seleccionar destino de exportación",
            f"{self.current_project.name}_resultados.csv",
            "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;SQLite (*.db)"
        )
        if file_path:
            self.exp_path_input.setText(file_path)

    def sync_ui_to_project(self):
        """Lee los valores visuales de la interfaz y actualiza el modelo ProjectConfig."""
        self.current_project.name = self.proj_name_input.text().strip() or "Proyecto_UltraScrape"

        # URLs
        urls = []
        main_url = self.start_url_input.text().strip()
        if main_url:
            urls.append(main_url)
        for line in self.multi_url_edit.toPlainText().splitlines():
            line = line.strip()
            if line and line not in urls:
                urls.append(line)
        self.current_project.start_urls = urls

        # Dinámico
        self.current_project.dynamic.use_javascript = self.js_check.isChecked()
        self.current_project.dynamic.headless = self.headless_check.isChecked()
        self.current_project.dynamic.scroll_infinite = self.scroll_check.isChecked()
        self.current_project.dynamic.max_scrolls = self.max_scrolls_spin.value()
        self.current_project.dynamic.scroll_delay_sec = self.scroll_delay_spin.value()
        self.current_project.dynamic.load_more_selector = self.load_more_input.text().strip() or None
        self.current_project.dynamic.wait_selector = self.wait_sel_input.text().strip() or None

        # Paginación
        self.current_project.pagination.enabled = self.pag_enable_check.isChecked()
        self.current_project.pagination.pagination_type = (
            "next_button" if self.pag_type_combo.currentIndex() == 0 else "url_pattern"
        )
        self.current_project.pagination.next_selector = self.next_sel_input.text().strip()
        self.current_project.pagination.pattern_template = self.pattern_input.text().strip()
        self.current_project.pagination.max_pages = self.max_pages_spin.value()

        # Procesador
        self.current_project.processor.deduplicate = self.dedup_check.isChecked()
        self.current_project.processor.trim_spaces = self.trim_check.isChecked()
        self.current_project.processor.normalize_prices = self.price_norm_check.isChecked()
        self.current_project.processor.convert_dates = self.date_norm_check.isChecked()
        self.current_project.processor.validate_urls = self.url_val_check.isChecked()
        self.current_project.processor.drop_incomplete = self.drop_incomp_check.isChecked()

        # Red / Control
        self.current_project.settings.delay_between_requests = self.delay_spin.value()
        self.current_project.settings.max_records = self.max_records_spin.value()
        self.current_project.settings.timeout_sec = self.timeout_spin.value()
        self.current_project.settings.max_retries = self.retries_spin.value()

        # Exportación
        fmt = "csv"
        idx = self.exp_format_combo.currentIndex()
        if idx == 1: fmt = "xlsx"
        elif idx == 2: fmt = "json"
        elif idx == 3: fmt = "sqlite"

        self.current_project.export.format = fmt
        self.current_project.export.output_path = self.exp_path_input.text().strip()

    def load_project_to_ui(self, cfg: ProjectConfig):
        """Carga un objeto ProjectConfig en todos los campos visuales."""
        self.current_project = cfg
        self.proj_name_input.setText(cfg.name)

        if cfg.start_urls:
            self.start_url_input.setText(cfg.start_urls[0])
            self.multi_url_edit.setText("\n".join(cfg.start_urls))
        else:
            self.start_url_input.clear()
            self.multi_url_edit.clear()

        self.js_check.setChecked(cfg.dynamic.use_javascript)
        self.headless_check.setChecked(cfg.dynamic.headless)
        self.scroll_check.setChecked(cfg.dynamic.scroll_infinite)
        self.max_scrolls_spin.setValue(cfg.dynamic.max_scrolls)
        self.scroll_delay_spin.setValue(cfg.dynamic.scroll_delay_sec)
        self.load_more_input.setText(cfg.dynamic.load_more_selector or "")
        self.wait_sel_input.setText(cfg.dynamic.wait_selector or "")

        self.pag_enable_check.setChecked(cfg.pagination.enabled)
        self.pag_type_combo.setCurrentIndex(0 if cfg.pagination.pagination_type == "next_button" else 1)
        self.next_sel_input.setText(cfg.pagination.next_selector)
        self.pattern_input.setText(cfg.pagination.pattern_template)
        self.max_pages_spin.setValue(cfg.pagination.max_pages)

        self.dedup_check.setChecked(cfg.processor.deduplicate)
        self.trim_check.setChecked(cfg.processor.trim_spaces)
        self.price_norm_check.setChecked(cfg.processor.normalize_prices)
        self.date_norm_check.setChecked(cfg.processor.convert_dates)
        self.url_val_check.setChecked(cfg.processor.validate_urls)
        self.drop_incomp_check.setChecked(cfg.processor.drop_incomplete)

        self.delay_spin.setValue(cfg.settings.delay_between_requests)
        self.max_records_spin.setValue(cfg.settings.max_records)
        self.timeout_spin.setValue(int(cfg.settings.timeout_sec))
        self.retries_spin.setValue(cfg.settings.max_retries)

        self.exp_path_input.setText(cfg.export.output_path)
        self.refresh_selectors_table()

    def new_project(self):
        self.current_project = ProjectConfig(name="Nuevo_Proyecto")
        self.load_project_to_ui(self.current_project)
        self.results_widget.clear_results()
        self.log("✨ Nuevo proyecto iniciado.")

    def save_project(self):
        self.sync_ui_to_project()
        saved_path = self.project_manager.save_project(self.current_project)
        QMessageBox.information(self, "Proyecto Guardado", f"Configuración guardada exitosamente en:\n{saved_path}")
        self.log(f"💾 Proyecto '{self.current_project.name}' guardado.")

    def open_project_dialog(self):
        dlg = ProjectDialog(self.project_manager, self)
        if dlg.exec() and dlg.selected_config:
            self.load_project_to_ui(dlg.selected_config)
            self.results_widget.clear_results()
            self.log(f"📂 Proyecto '{dlg.selected_config.name}' cargado.")

    def start_scraping(self):
        self.sync_ui_to_project()

        if not self.current_project.start_urls:
            QMessageBox.warning(self, "Atención", "Por favor introduce al menos una URL inicial.")
            return

        if not self.current_project.selectors:
            QMessageBox.warning(self, "Atención", "Agrega al menos un selector para extraer.")
            return

        # Si el usuario seleccionó JS dinámico y Playwright no está disponible, avisarle
        if self.current_project.dynamic.use_javascript:
            from core.browser import PlaywrightBrowser
            if not PlaywrightBrowser.is_available():
                QMessageBox.critical(
                    self,
                    "Playwright requerido",
                    "Has activado JavaScript dinámico pero Playwright no está instalado.\n"
                    "Ejecuta en consola:\npip install playwright && playwright install"
                )
                return

        self.results_widget.clear_results()
        self.results_widget.set_headers([s.name for s in self.current_project.selectors])

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.progress_bar.setFormat("Scraping en curso...")
        self.progress_bar.setValue(10)
        self.status_label.setText("Estado: Extrayendo...")

        # Iniciar Worker QThread
        self.worker = ScraperWorker(self.current_project, self)
        self.worker.sig_item_scraped.connect(self.results_widget.add_item)
        self.worker.sig_stats_updated.connect(self.handle_stats_update)
        self.worker.sig_log.connect(self.log)
        self.worker.sig_finished.connect(self.handle_scraping_finished)
        self.worker.sig_error.connect(self.handle_scraping_error)
        self.worker.start()

    def handle_stats_update(self, stats: ScrapeStats):
        self.results_widget.update_stats(stats)
        self.status_label.setText(
            f"Estado: {stats.status_text} | Páginas: {stats.pages_scraped} | Registros: {stats.records_found} | Errores: {stats.errors_count}"
        )
        if stats.pages_scraped > 0:
            target_pages = self.current_project.pagination.max_pages if self.current_project.pagination.enabled else len(self.current_project.start_urls)
            pct = min(int((stats.pages_scraped / max(target_pages, 1)) * 100), 99)
            self.progress_bar.setValue(pct)
            self.progress_bar.setFormat(f"{pct}% - {stats.records_found} registros ({stats.current_speed} pág/s)")

    def toggle_pause(self):
        if not self.worker:
            return
        if self.worker.engine.is_paused:
            self.worker.resume()
            self.pause_btn.setText("⏸️ PAUSAR")
        else:
            self.worker.pause()
            self.pause_btn.setText("▶️ REANUDAR")

    def stop_scraping(self):
        if self.worker:
            self.worker.stop()
            self.log("🛑 Detención solicitada por el usuario...")

    def handle_scraping_finished(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Scraping Finalizado")
        self.status_label.setText("Estado: Finalizado")

        # Auto-exportación si está configurado archivo destino
        if self.current_project.export.output_path and self.results_widget.items:
            self.auto_export_results()

    def auto_export_results(self):
        out_path = self.current_project.export.output_path
        fmt = self.current_project.export.format.lower()
        items = self.results_widget.items

        try:
            if fmt == "csv":
                from exporters.csv_exporter import CsvExporter
                CsvExporter(out_path).export(items)
            elif fmt == "xlsx":
                from exporters.excel_exporter import ExcelExporter
                ExcelExporter(out_path).export(items)
            elif fmt == "json":
                from exporters.json_exporter import JsonExporter
                JsonExporter(out_path).export(items)
            elif fmt == "sqlite":
                from exporters.sqlite_exporter import SqliteExporter
                SqliteExporter(out_path).export(items)

            self.log(f"📦 Resultados auto-exportados en: {out_path}")
        except Exception as e:
            self.log(f"⚠️ Error en auto-exportación: {e}")

    def handle_scraping_error(self, err_msg: str):
        self.log(f"❌ Error en proceso: {err_msg}")
        QMessageBox.critical(self, "Error de Scraping", err_msg)
        self.handle_scraping_finished()
