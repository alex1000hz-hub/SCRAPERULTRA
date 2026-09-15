"""
UltraScrape - Diálogo de Configuración y Prueba en Vivo de Selectores
"""
from typing import Optional
from core.models import SelectorConfig
from core.extractor import Extractor
import requests

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QComboBox, QCheckBox, QPushButton, QMessageBox, QTextEdit,
        QFormLayout, QGroupBox
    )
    from PySide6.QtCore import Qt
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    class QDialog:
        pass


class SelectorDialog(QDialog):
    def __init__(self, selector_config: Optional[SelectorConfig] = None, test_url: str = "", parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.setWindowTitle("Configurar Selector / Extractor")
        self.resize(550, 520)

        self.selector_config = selector_config
        self.test_url = test_url
        self.extractor = Extractor(test_url)

        self.init_ui()
        if selector_config:
            self.load_config(selector_config)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        # Formulario principal
        form_group = QGroupBox("Propiedades del Campo")
        form_layout = QFormLayout(form_group)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ej. nombre, precio, imagen, descripción")
        form_layout.addRow("Nombre del Campo:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["CSS", "XPath"])
        form_layout.addRow("Tipo de Selector:", self.type_combo)

        self.selector_input = QLineEdit()
        self.selector_input.setPlaceholderText("ej. .product-title, h1, //div[@class='price']")
        form_layout.addRow("Selector:", self.selector_input)

        self.attr_combo = QComboBox()
        self.attr_combo.setEditable(True)
        self.attr_combo.addItems(["text", "href", "src", "html", "alt", "title", "value"])
        form_layout.addRow("Atributo a Extraer:", self.attr_combo)

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Opcional: regex para filtrar ej: \\d+(\\.\\d+)?")
        form_layout.addRow("Filtro Regex (Opcional):", self.regex_input)

        self.default_input = QLineEdit()
        self.default_input.setPlaceholderText("Valor si no se encuentra")
        form_layout.addRow("Valor por Defecto:", self.default_input)

        self.required_check = QCheckBox("Obligatorio (descartar registro si está vacío)")
        form_layout.addRow("", self.required_check)

        main_layout.addWidget(form_group)

        # Probador en vivo
        test_group = QGroupBox("Probador en Vivo (Instant Preview)")
        test_layout = QVBoxLayout(test_group)

        url_box = QHBoxLayout()
        self.test_url_input = QLineEdit(self.test_url)
        self.test_url_input.setPlaceholderText("URL objetivo para probar el selector...")
        test_btn = QPushButton("🔍 Probar Selector")
        test_btn.setObjectName("accentBtn")
        test_btn.clicked.connect(self.run_live_test)

        url_box.addWidget(self.test_url_input)
        url_box.addWidget(test_btn)
        test_layout.addLayout(url_box)

        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setPlaceholderText("Los resultados de la prueba aparecerán aquí...")
        self.test_output.setMaximumHeight(120)
        test_layout.addWidget(self.test_output)

        main_layout.addWidget(test_group)

        # Botones Guardar / Cancelar
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar Selector")
        save_btn.setObjectName("startBtn")
        save_btn.clicked.connect(self.save_and_accept)
        btn_box.addWidget(save_btn)

        main_layout.addLayout(btn_box)

    def load_config(self, cfg: SelectorConfig):
        self.name_input.setText(cfg.name)
        self.type_combo.setCurrentText(cfg.selector_type.upper())
        self.selector_input.setText(cfg.selector)
        self.attr_combo.setCurrentText(cfg.attribute)
        self.regex_input.setText(cfg.regex or "")
        self.default_input.setText(cfg.default_value)
        self.required_check.setChecked(cfg.required)

    def run_live_test(self):
        url = self.test_url_input.text().strip()
        selector = self.selector_input.text().strip()
        sel_type = self.type_combo.currentText().lower()
        attribute = self.attr_combo.currentText().strip()
        regex_pattern = self.regex_input.text().strip() or None

        if not url:
            QMessageBox.warning(self, "Atención", "Por favor ingresa una URL para probar.")
            return
        if not selector:
            QMessageBox.warning(self, "Atención", "Por favor ingresa un selector.")
            return

        self.test_output.setText("Cargando y evaluando selector...")
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"},
                timeout=12
            )
            resp.encoding = resp.apparent_encoding or "utf-8"
            html = resp.text

            test_cfg = SelectorConfig(
                name=self.name_input.text().strip() or "test",
                selector=selector,
                selector_type=sel_type,
                attribute=attribute,
                regex=regex_pattern,
                is_multiple=True
            )

            results = self.extractor.extract_single_field(html, None, test_cfg, base_url=url)
            if isinstance(results, list):
                if not results:
                    self.test_output.setText("⚠️ 0 coincidencias encontradas. Verifica el selector.")
                else:
                    preview = "\n".join(f"[{i+1}] {val}" for i, val in enumerate(results[:10]))
                    if len(results) > 10:
                        preview += f"\n... y {len(results)-10} más (Total: {len(results)})"
                    self.test_output.setText(f"✅ Éxito ({len(results)} encontrados):\n\n{preview}")
            else:
                self.test_output.setText(f"✅ Resultado:\n{results}")

        except Exception as e:
            self.test_output.setText(f"❌ Error al evaluar: {str(e)}")

    def save_and_accept(self):
        name = self.name_input.text().strip()
        selector = self.selector_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Campo Requerido", "El campo 'Nombre' es obligatorio.")
            return
        if not selector:
            QMessageBox.warning(self, "Campo Requerido", "El campo 'Selector' es obligatorio.")
            return

        self.selector_config = SelectorConfig(
            name=name,
            selector=selector,
            selector_type=self.type_combo.currentText().lower(),
            attribute=self.attr_combo.currentText().strip(),
            regex=self.regex_input.text().strip() or None,
            default_value=self.default_input.text().strip(),
            required=self.required_check.isChecked()
        )
        self.accept()

    def get_config(self) -> SelectorConfig:
        return self.selector_config
