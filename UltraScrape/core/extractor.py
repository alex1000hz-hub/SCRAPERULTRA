"""
UltraScrape - Motor de Extracción CSS y XPath
"""
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
try:
    from lxml import html as lxml_html
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

from .models import SelectorConfig


class Extractor:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    def parse(self, html_content: str) -> BeautifulSoup:
        """Parsea el HTML con BeautifulSoup utilizando lxml o html.parser."""
        parser = "lxml" if LXML_AVAILABLE else "html.parser"
        return BeautifulSoup(html_content, parser)

    def extract_element_value(self, element: Any, attribute: str, base_url: str = "") -> str:
        """Extrae el texto o un atributo específico de un elemento BS4."""
        if not element:
            return ""

        url_to_use = base_url or self.base_url
        attr_lower = attribute.lower().strip()

        if attr_lower in ("text", "innertext", "string"):
            val = element.get_text(separator=" ", strip=True)
        elif attr_lower in ("html", "outerhtml"):
            val = str(element)
        elif attr_lower == "innerhtml":
            val = "".join(str(c) for c in element.children)
        else:
            # Atributo HTML común (href, src, data-*, alt, title, etc.)
            val = element.get(attribute, "")
            if isinstance(val, list):
                val = " ".join(val)
            val = str(val).strip()

            # Si es enlace o imagen relativo, convertir a absoluto
            if attr_lower in ("href", "src") and val and url_to_use:
                val = urljoin(url_to_use, val)

        return val

    def extract_by_css(
        self,
        soup: BeautifulSoup,
        selector: str,
        attribute: str = "text",
        is_multiple: bool = False,
        base_url: str = ""
    ) -> Any:
        """Ejecuta una consulta CSS Selector."""
        try:
            elements = soup.select(selector)
        except Exception:
            return [] if is_multiple else ""

        if not elements:
            return [] if is_multiple else ""

        if is_multiple:
            return [
                self.extract_element_value(el, attribute, base_url)
                for el in elements
            ]
        else:
            return self.extract_element_value(elements[0], attribute, base_url)

    def extract_by_xpath(
        self,
        html_content: str,
        xpath_query: str,
        attribute: str = "text",
        is_multiple: bool = False,
        base_url: str = ""
    ) -> Any:
        """Ejecuta una consulta XPath utilizando lxml."""
        if not LXML_AVAILABLE:
            return [] if is_multiple else "[Error: lxml no disponible]"

        try:
            tree = lxml_html.fromstring(html_content)
            results = tree.xpath(xpath_query)
        except Exception as e:
            return [] if is_multiple else f"[Error XPath: {str(e)}]"

        if not results:
            return [] if is_multiple else ""

        url_to_use = base_url or self.base_url

        def format_xpath_item(item: Any) -> str:
            if isinstance(item, str):
                val = item.strip()
            elif hasattr(item, "text_content"):
                if attribute.lower() in ("text", "innertext"):
                    val = item.text_content().strip()
                elif attribute in item.attrib:
                    val = item.attrib[attribute].strip()
                else:
                    val = item.text_content().strip()
            else:
                val = str(item).strip()

            if attribute.lower() in ("href", "src") and val and url_to_use:
                val = urljoin(url_to_use, val)
            return val

        if is_multiple:
            return [format_xpath_item(it) for it in results]
        else:
            return format_xpath_item(results[0])

    def extract_single_field(
        self,
        html_content: str,
        soup: Optional[BeautifulSoup],
        config: SelectorConfig,
        base_url: str = ""
    ) -> Any:
        """Extrae un único campo respetando su tipo de selector y expresiones regulares."""
        if soup is None:
            soup = self.parse(html_content)

        url_to_use = base_url or self.base_url

        if config.selector_type.lower() == "xpath":
            val = self.extract_by_xpath(
                html_content=html_content,
                xpath_query=config.selector,
                attribute=config.attribute,
                is_multiple=config.is_multiple,
                base_url=url_to_use
            )
        else:
            val = self.extract_by_css(
                soup=soup,
                selector=config.selector,
                attribute=config.attribute,
                is_multiple=config.is_multiple,
                base_url=url_to_use
            )

        # Aplicar regex si está configurado
        if config.regex:
            try:
                pattern = re.compile(config.regex)
                if isinstance(val, list):
                    processed_list = []
                    for item in val:
                        match = pattern.search(str(item))
                        processed_list.append(match.group(1) if match and match.groups() else (match.group(0) if match else ""))
                    val = processed_list
                else:
                    match = pattern.search(str(val))
                    val = match.group(1) if match and match.groups() else (match.group(0) if match else "")
            except Exception:
                pass

        if not val and config.default_value:
            val = config.default_value

        return val

    def extract_items_from_containers(
        self,
        html_content: str,
        container_selector: str,
        selectors: List[SelectorConfig],
        base_url: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Extrae registros tabulares repitiendo los selectores dentro de cada contenedor
        (ej. tarjetas de productos `.product-card`).
        """
        soup = self.parse(html_content)
        url_to_use = base_url or self.base_url
        containers = soup.select(container_selector) if container_selector else []

        if not containers:
            # Si no hay contenedor especificado, extraer como lista alineada
            return self.extract_aligned_records(html_content, soup, selectors, url_to_use)

        records = []
        for container in containers:
            record: Dict[str, Any] = {}
            for sel in selectors:
                if sel.selector_type.lower() == "css":
                    elements = container.select(sel.selector)
                    if elements:
                        val = self.extract_element_value(elements[0], sel.attribute, url_to_use)
                    else:
                        val = sel.default_value
                else:
                    # Fallback xpath dentro del contenedor
                    val = sel.default_value

                if sel.regex and val:
                    try:
                        m = re.search(sel.regex, str(val))
                        val = m.group(1) if m and m.groups() else (m.group(0) if m else "")
                    except Exception:
                        pass

                record[sel.name] = val
            records.append(record)

        return records

    def extract_aligned_records(
        self,
        html_content: str,
        soup: BeautifulSoup,
        selectors: List[SelectorConfig],
        base_url: str = ""
    ) -> List[Dict[str, Any]]:
        """Extrae listas independientes para cada campo y las alinea por índice."""
        extracted_columns: Dict[str, List[Any]] = {}
        max_len = 0

        for sel in selectors:
            vals = self.extract_single_field(
                html_content=html_content,
                soup=soup,
                config=SelectorConfig(
                    name=sel.name,
                    selector=sel.selector,
                    selector_type=sel.selector_type,
                    attribute=sel.attribute,
                    regex=sel.regex,
                    default_value=sel.default_value,
                    is_multiple=True
                ),
                base_url=base_url
            )
            if not isinstance(vals, list):
                vals = [vals] if vals else []
            extracted_columns[sel.name] = vals
            if len(vals) > max_len:
                max_len = len(vals)

        if max_len == 0:
            # Intento de extracción como página de 1 solo registro (ej. página de detalle de producto)
            single_record: Dict[str, Any] = {}
            has_data = False
            for sel in selectors:
                val = self.extract_single_field(html_content, soup, sel, base_url)
                single_record[sel.name] = val
                if val:
                    has_data = True
            return [single_record] if has_data else []

        records = []
        for i in range(max_len):
            row: Dict[str, Any] = {}
            for sel in selectors:
                col = extracted_columns.get(sel.name, [])
                row[sel.name] = col[i] if i < len(col) else sel.default_value
            records.append(row)

        return records
