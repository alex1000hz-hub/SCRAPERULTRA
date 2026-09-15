"""
UltraScrape Core Engine Package
"""
from .models import SelectorConfig, ScrapingSettings, ProjectConfig, ScrapedItem, ScrapeStats
from .extractor import Extractor
from .processor import DataProcessor
from .pagination import PaginationManager
from .browser import PlaywrightBrowser
from .crawler import ScraperEngine

__all__ = [
    "SelectorConfig",
    "ScrapingSettings",
    "ProjectConfig",
    "ScrapedItem",
    "ScrapeStats",
    "Extractor",
    "DataProcessor",
    "PaginationManager",
    "PlaywrightBrowser",
    "ScraperEngine"
]
