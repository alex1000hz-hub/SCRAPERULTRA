"""
UltraScrape - Modelos de Datos y Configuraciones
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import uuid


@dataclass
class SelectorConfig:
    name: str
    selector: str
    selector_type: str = "css"  # "css" o "xpath"
    attribute: str = "text"      # "text", "href", "src", "html", "value" u otro atributo HTML
    regex: Optional[str] = None
    default_value: str = ""
    is_multiple: bool = False
    required: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class DynamicConfig:
    use_javascript: bool = False
    headless: bool = True
    scroll_infinite: bool = False
    max_scrolls: int = 5
    scroll_delay_sec: float = 1.0
    wait_selector: Optional[str] = None
    wait_timeout_sec: float = 10.0
    load_more_selector: Optional[str] = None
    load_more_clicks: int = 3


@dataclass
class PaginationConfig:
    enabled: bool = False
    pagination_type: str = "next_button"  # "next_button", "url_pattern", "infinite_scroll"
    next_selector: str = ""
    pattern_template: str = ""           # ej. https://ejemplo.com/cat?page={page}
    start_page: int = 1
    max_pages: int = 5


@dataclass
class ProcessorConfig:
    deduplicate: bool = True
    deduplicate_by: str = ""             # Campo clave o vacío para hash completo
    trim_spaces: bool = True
    normalize_prices: bool = True
    convert_dates: bool = False
    validate_urls: bool = True
    drop_incomplete: bool = False
    required_fields: List[str] = field(default_factory=list)


@dataclass
class ExportConfig:
    format: str = "csv"                  # "csv", "xlsx", "json", "sqlite"
    output_path: str = ""
    table_name: str = "scraped_data"     # Para SQLite


@dataclass
class ScrapingSettings:
    concurrency: int = 2
    delay_between_requests: float = 1.0
    timeout_sec: float = 20.0
    max_retries: int = 3
    max_records: int = 1000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProjectConfig:
    name: str = "Nuevo Proyecto"
    description: str = ""
    start_urls: List[str] = field(default_factory=list)
    selectors: List[SelectorConfig] = field(default_factory=list)
    dynamic: DynamicConfig = field(default_factory=DynamicConfig)
    pagination: PaginationConfig = field(default_factory=PaginationConfig)
    processor: ProcessorConfig = field(default_factory=ProcessorConfig)
    settings: ScrapingSettings = field(default_factory=ScrapingSettings)
    export: ExportConfig = field(default_factory=ExportConfig)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        selectors = [
            SelectorConfig(**s) for s in data.get("selectors", [])
        ]
        dynamic = DynamicConfig(**data.get("dynamic", {}))
        pagination = PaginationConfig(**data.get("pagination", {}))
        processor = ProcessorConfig(**data.get("processor", {}))
        settings = ScrapingSettings(**data.get("settings", {}))
        export = ExportConfig(**data.get("export", {}))
        
        return cls(
            name=data.get("name", "Nuevo Proyecto"),
            description=data.get("description", ""),
            start_urls=data.get("start_urls", []),
            selectors=selectors,
            dynamic=dynamic,
            pagination=pagination,
            processor=processor,
            settings=settings,
            export=export
        )

    def save_to_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "ProjectConfig":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class ScrapedItem:
    data: Dict[str, Any]
    source_url: str
    page_number: int = 1
    timestamp: str = ""
    is_valid: bool = True
    error_note: Optional[str] = None


@dataclass
class ScrapeStats:
    pages_scraped: int = 0
    records_found: int = 0
    errors_count: int = 0
    current_speed: float = 0.0 # páginas / seg
    elapsed_seconds: float = 0.0
    status_text: str = "Listo"
    is_running: bool = False
    is_paused: bool = False
