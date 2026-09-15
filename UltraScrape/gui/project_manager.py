"""
UltraScrape - Administrador de Proyectos (Guardar, Cargar, Duplicar)
"""
import os
import json
import re
from typing import List, Optional
from core.models import ProjectConfig

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
        QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    class QDialog:
        pass


class ProjectManager:
    def __init__(self, base_projects_dir: str):
        self.base_dir = os.path.abspath(base_projects_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def list_projects(self) -> List[str]:
        """Devuelve la lista de nombres de proyectos disponibles."""
        if not os.path.exists(self.base_dir):
            return []
        projects = []
        for item in os.listdir(self.base_dir):
            p_dir = os.path.join(self.base_dir, item)
            if os.path.isdir(p_dir) and os.path.exists(os.path.join(p_dir, "config.json")):
                projects.append(item)
        return sorted(projects)

    def save_project(self, config: ProjectConfig) -> str:
        """Guarda un proyecto en su carpeta correspondiente."""
        folder_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', config.name.lower()).strip('_') or "default_project"
        project_dir = os.path.join(self.base_dir, folder_name)
        results_dir = os.path.join(project_dir, "results")
        os.makedirs(results_dir, exist_ok=True)

        config_path = os.path.join(project_dir, "config.json")
        config.save_to_file(config_path)
        return config_path

    def load_project(self, project_name: str) -> Optional[ProjectConfig]:
        """Carga la configuración de un proyecto."""
        config_path = os.path.join(self.base_dir, project_name, "config.json")
        if not os.path.exists(config_path):
            return None
        return ProjectConfig.load_from_file(config_path)


class ProjectDialog(QDialog):
    def __init__(self, manager: ProjectManager, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.manager = manager
        self.selected_config: Optional[ProjectConfig] = None

        self.setWindowTitle("Gestor de Proyectos - UltraScrape")
        self.resize(450, 380)
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Selecciona un proyecto guardado:"))

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.load_selected)
        layout.addWidget(self.list_widget)

        btn_box = QHBoxLayout()

        load_btn = QPushButton("📂 Abrir Proyecto")
        load_btn.setObjectName("accentBtn")
        load_btn.clicked.connect(self.load_selected)
        btn_box.addWidget(load_btn)

        del_btn = QPushButton("🗑️ Eliminar")
        del_btn.clicked.connect(self.delete_selected)
        btn_box.addWidget(del_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.reject)
        btn_box.addWidget(close_btn)

        layout.addLayout(btn_box)

    def refresh_list(self):
        self.list_widget.clear()
        for p in self.manager.list_projects():
            self.list_widget.addItem(p)

    def load_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un proyecto de la lista.")
            return

        cfg = self.manager.load_project(item.text())
        if cfg:
            self.selected_config = cfg
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo leer la configuración del proyecto.")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Estás seguro de eliminar el proyecto '{item.text()}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            p_dir = os.path.join(self.manager.base_dir, item.text())
            import shutil
            shutil.rmtree(p_dir, ignore_errors=True)
            self.refresh_list()
