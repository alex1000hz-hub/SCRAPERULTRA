"""
UltraScrape - Motor Principal de Scraping y Orquestación de Crawling
"""
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import requests

from .models import ProjectConfig, ScrapedItem, ScrapeStats
from .extractor import Extractor
from .processor import DataProcessor
from .pagination import PaginationManager
from .browser import PlaywrightBrowser


class ScraperEngine:
    def __init__(self, project_config: ProjectConfig):
        self.config = project_config
        self.extractor = Extractor()
        self.processor = DataProcessor(self.config.processor)
        self.pagination = PaginationManager(self.config.pagination)
        self.browser: Optional[PlaywrightBrowser] = None

        # Estado del proceso
        self.stats = ScrapeStats()
        self.is_running = False
        self.is_paused = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # No pausado inicialmente

        # Callbacks para la GUI
        self.on_item_scraped: Optional[Callable[[ScrapedItem], None]] = None
        self.on_stats_changed: Optional[Callable[[ScrapeStats], None]] = None
        self.on_log_message: Optional[Callable[[str], None]] = None
        self.on_finished: Optional[Callable[[], None]] = None

        # Almacenamiento en memoria de resultados
        self.scraped_items: List[ScrapedItem] = []

    def log(self, message: str) -> None:
        """Emite un mensaje de registro."""
        if self.on_log_message:
            self.on_log_message(message)

    def update_stats(self) -> None:
        """Actualiza y notifica las métricas de scraping."""
        if self.on_stats_changed:
            self.on_stats_changed(self.stats)

    def pause(self) -> None:
        """Pausa temporalmente el proceso."""
        self.is_paused = True
        self.stats.is_paused = True
        self.stats.status_text = "Pausado"
        self._pause_event.clear()
        self.log("⏸️ Scraping pausado.")
        self.update_stats()

    def resume(self) -> None:
        """Reanuda el proceso pausado."""
        self.is_paused = False
        self.stats.is_paused = False
        self.stats.status_text = "Scraping..."
        self._pause_event.set()
        self.log("▶️ Scraping reanudado.")
        self.update_stats()

    def stop(self) -> None:
        """Detiene de forma segura el proceso."""
        self.is_running = False
        self.stats.is_running = False
        self.stats.status_text = "Detenido"
        self._stop_event.set()
        self._pause_event.set()  # Desbloquear si estaba pausado para poder salir
        self.log("🛑 Deteniendo proceso de scraping...")
        self.update_stats()

    def _fetch_html_static(self, url: str) -> str:
        """Descarga el HTML usando requests con reintentos y configuración personalizada."""
        headers = self.config.settings.headers.copy()
        if "User-Agent" not in headers:
            headers["User-Agent"] = self.config.settings.user_agent

        for attempt in range(1, self.config.settings.max_retries + 1):
            if self._stop_event.is_set():
                return ""
            try:
                resp = requests.get(
                    url,
                    headers=headers,
                    cookies=self.config.settings.cookies,
                    timeout=self.config.settings.timeout_sec
                )
                resp.raise_for_status()
                # Detección automática de codificación
                resp.encoding = resp.apparent_encoding or "utf-8"
                return resp.text
            except Exception as e:
                self.log(f"⚠️ Reintento {attempt}/{self.config.settings.max_retries} en {url}: {e}")
                if attempt < self.config.settings.max_retries:
                    time.sleep(self.config.settings.delay_between_requests)
                else:
                    self.stats.errors_count += 1
                    self.log(f"❌ Error al cargar {url}: {e}")
                    raise

        return ""

    def _fetch_html(self, url: str) -> str:
        """Obtiene el HTML usando Playwright o Requests según la configuración dinámica."""
        if self.config.dynamic.use_javascript:
            if not self.browser:
                self.browser = PlaywrightBrowser(self.config.dynamic, self.config.settings)
            try:
                return self.browser.fetch_page_content(url)
            except Exception as e:
                self.stats.errors_count += 1
                self.log(f"❌ Error de Playwright en {url}: {e}")
                return ""
        else:
            return self._fetch_html_static(url)

    def scrape_url(self, url: str, page_number: int = 1) -> List[ScrapedItem]:
        """Extrae y procesa los registros de una sola URL."""
        self._pause_event.wait()
        if self._stop_event.is_set():
            return []

        self.log(f"🌐 Extrayendo página {page_number}: {url}")
        html = self._fetch_html(url)
        if not html:
            return []

        soup = self.extractor.parse(html)
        raw_records = self.extractor.extract_aligned_records(
            html_content=html,
            soup=soup,
            selectors=self.config.selectors,
            base_url=url
        )

        valid_items: List[ScrapedItem] = []
        for raw in raw_records:
            item = self.processor.process_record(raw, source_url=url, page_number=page_number)
            if item:
                valid_items.append(item)
                self.scraped_items.append(item)
                self.stats.records_found += 1
                if self.on_item_scraped:
                    self.on_item_scraped(item)

                if self.config.settings.max_records > 0 and self.stats.records_found >= self.config.settings.max_records:
                    self.log(f"🎯 Límite de {self.config.settings.max_records} registros alcanzado.")
                    self.stop()
                    break

        self.stats.pages_scraped += 1
        return valid_items

    def run(self) -> None:
        """Ejecuta el ciclo principal de crawling."""
        self.is_running = True
        self.stats = ScrapeStats(is_running=True, status_text="Scraping...")
        self._stop_event.clear()
        self._pause_event.set()
        self.scraped_items.clear()
        self.processor.reset_state()

        start_time = time.time()
        self.log(f"🚀 Iniciando UltraScrape para el proyecto '{self.config.name}'")
        self.update_stats()

        try:
            urls_to_crawl: List[str] = list(self.config.start_urls)

            # Si la paginación por patrón está activa, generar URLs adicionales
            if self.config.pagination.enabled and self.config.pagination.pagination_type == "url_pattern":
                for p_url in self.pagination.generate_pattern_urls():
                    if p_url not in urls_to_crawl:
                        urls_to_crawl.append(p_url)

            current_page = 1

            for url in urls_to_crawl:
                if self._stop_event.is_set():
                    break

                self.scrape_url(url, page_number=current_page)
                current_page += 1

                # Métricas de velocidad
                elapsed = time.time() - start_time
                self.stats.elapsed_seconds = elapsed
                if elapsed > 0:
                    self.stats.current_speed = round(self.stats.pages_scraped / elapsed, 2)
                self.update_stats()

                # Delay entre peticiones
                if self.config.settings.delay_between_requests > 0 and not self._stop_event.is_set():
                    time.sleep(self.config.settings.delay_between_requests)

            self.stats.status_text = "Completado"
            self.log(
                f"✅ Scraping finalizado. {self.stats.records_found} registros, "
                f"{self.stats.pages_scraped} páginas, {self.stats.errors_count} errores."
            )

        except Exception as e:
            self.stats.status_text = "Error"
            self.log(f"💥 Error crítico durante el scraping: {e}")
        finally:
            self.is_running = False
            self.stats.is_running = False
            if self.browser:
                self.browser.stop()
                self.browser = None
            self.update_stats()
            if self.on_finished:
                self.on_finished()
