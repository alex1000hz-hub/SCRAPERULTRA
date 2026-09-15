"""
UltraScrape - Integración de Navegador Dinámico con Playwright
"""
import time
from typing import Optional, Dict, Any
from .models import DynamicConfig, ScrapingSettings

try:
    from playwright.sync_api import sync_playwright, Browser, Page, Playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    Browser = Any
    Page = Any
    Playwright = Any


class PlaywrightBrowser:
    def __init__(self, dynamic_config: DynamicConfig, settings: ScrapingSettings):
        self.dynamic_config = dynamic_config
        self.settings = settings
        self._pw: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    @staticmethod
    def is_available() -> bool:
        return PLAYWRIGHT_AVAILABLE

    def start(self) -> None:
        """Inicia la instancia de Playwright Chromium."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright no está instalado. Ejecute: pip install playwright && playwright install"
            )

        if not self._pw:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(
                headless=self.dynamic_config.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )

    def stop(self) -> None:
        """Cierra el navegador y libera recursos."""
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._pw = None

    def fetch_page_content(self, url: str) -> str:
        """
        Navega a la URL con Playwright, ejecuta scroll infinito o clics en 'Cargar más',
        espera los selectores configurados y devuelve el HTML final renderizado.
        """
        if not self._browser:
            self.start()

        assert self._browser is not None

        # Configurar contexto de navegación con cookies y headers
        context = self._browser.new_context(
            user_agent=self.settings.user_agent,
            extra_http_headers=self.settings.headers
        )

        # Inyectar cookies si existen
        if self.settings.cookies:
            cookie_list = [
                {"name": k, "value": v, "url": url}
                for k, v in self.settings.cookies.items()
            ]
            try:
                context.add_cookies(cookie_list)
            except Exception:
                pass

        page: Page = context.new_page()
        try:
            # Navegación con timeout
            page.goto(url, timeout=int(self.settings.timeout_sec * 1000), wait_until="domcontentloaded")

            # 1. Espera de selector específico
            if self.dynamic_config.wait_selector:
                try:
                    page.wait_for_selector(
                        self.dynamic_config.wait_selector,
                        timeout=int(self.dynamic_config.wait_timeout_sec * 1000)
                    )
                except Exception:
                    pass

            # 2. Scroll infinito interactivo
            if self.dynamic_config.scroll_infinite:
                for _ in range(self.dynamic_config.max_scrolls):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(self.dynamic_config.scroll_delay_sec)

            # 3. Clics en botón 'Cargar más'
            if self.dynamic_config.load_more_selector:
                for _ in range(self.dynamic_config.load_more_clicks):
                    btn = page.query_selector(self.dynamic_config.load_more_selector)
                    if btn and btn.is_visible():
                        try:
                            btn.click()
                            time.sleep(self.dynamic_config.scroll_delay_sec)
                        except Exception:
                            break
                    else:
                        break

            # Breve pausa para asegurar renderizado final de JavaScript
            page.wait_for_timeout(500)
            html_content = page.content()
            return html_content

        finally:
            page.close()
            context.close()
