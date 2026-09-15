"""
UltraScrape - QThread Worker para Ejecución Asíncrona sin Bloquear la GUI
"""
from typing import Optional
from core.models import ProjectConfig, ScrapedItem, ScrapeStats
from core.crawler import ScraperEngine

try:
    from PySide6.QtCore import QThread, Signal
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    # Mock para permitir importación sin fallar si PySide6 aún no está en el path
    class QThread:
        pass
    def Signal(*args, **kwargs):
        return None


class ScraperWorker(QThread):
    # Definición de señales seguras entre subprocesos
    sig_item_scraped = Signal(object)      # ScrapedItem
    sig_stats_updated = Signal(object)     # ScrapeStats
    sig_log = Signal(str)                  # Mensaje de texto
    sig_finished = Signal()                # Finalización
    sig_error = Signal(str)                # Error crítico

    def __init__(self, project_config: ProjectConfig, parent=None):
        if PYSIDE_AVAILABLE:
            super().__init__(parent)
        self.config = project_config
        self.engine = ScraperEngine(self.config)

        # Conectar callbacks del motor a las señales de Qt
        self.engine.on_item_scraped = self._handle_item
        self.engine.on_stats_changed = self._handle_stats
        self.engine.on_log_message = self._handle_log
        self.engine.on_finished = self._handle_finish

    def _handle_item(self, item: ScrapedItem):
        if PYSIDE_AVAILABLE:
            self.sig_item_scraped.emit(item)

    def _handle_stats(self, stats: ScrapeStats):
        if PYSIDE_AVAILABLE:
            self.sig_stats_updated.emit(stats)

    def _handle_log(self, msg: str):
        if PYSIDE_AVAILABLE:
            self.sig_log.emit(msg)

    def _handle_finish(self):
        if PYSIDE_AVAILABLE:
            self.sig_finished.emit()

    def run(self):
        """Punto de entrada de ejecución en segundo plano."""
        try:
            self.engine.run()
        except Exception as e:
            if PYSIDE_AVAILABLE:
                self.sig_error.emit(str(e))

    def pause(self):
        self.engine.pause()

    def resume(self):
        self.engine.resume()

    def stop(self):
        self.engine.stop()
