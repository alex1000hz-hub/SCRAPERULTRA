"""
UltraScrape - Administrador de Paginación y Navegación
"""
from typing import Optional, Generator
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .models import PaginationConfig


class PaginationManager:
    def __init__(self, config: PaginationConfig, base_url: str = ""):
        self.config = config
        self.base_url = base_url
        self.current_page = config.start_page

    def generate_pattern_urls(self) -> Generator[str, None, None]:
        """Genera URLs secuenciales basadas en una plantilla ej: https://ejemplo.com?page={page}"""
        if not self.config.pattern_template:
            return

        end_page = self.config.start_page + self.config.max_pages
        for page_num in range(self.config.start_page, end_page):
            formatted_url = self.config.pattern_template.replace("{page}", str(page_num))
            yield formatted_url

    def find_next_page_url(self, soup: BeautifulSoup, current_page_url: str) -> Optional[str]:
        """Busca el enlace a la siguiente página mediante selector CSS o XPath."""
        if not self.config.next_selector:
            return None

        try:
            el = soup.select_one(self.config.next_selector)
            if not el:
                return None

            # Si es una etiqueta <a> con href
            if el.name == "a" and el.get("href"):
                next_href = el["href"].strip()
                return urljoin(current_page_url or self.base_url, next_href)

            # Si el elemento contiene un <a> hijo
            nested_a = el.find("a")
            if nested_a and nested_a.get("href"):
                return urljoin(current_page_url or self.base_url, nested_a["href"].strip())

            # Si tiene atributo data-href o data-url
            data_url = el.get("data-href") or el.get("data-url")
            if data_url:
                return urljoin(current_page_url or self.base_url, data_url.strip())

        except Exception:
            return None

        return None
