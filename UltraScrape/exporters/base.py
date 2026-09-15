"""
UltraScrape - Clase Base de Exportación
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.models import ScrapedItem


class BaseExporter(ABC):
    def __init__(self, output_path: str):
        self.output_path = output_path

    @abstractmethod
    def export(self, items: List[ScrapedItem]) -> bool:
        """Exporta la lista de items al destino configurado."""
        pass

    @staticmethod
    def items_to_dict_list(items: List[ScrapedItem]) -> List[Dict[str, Any]]:
        """Convierte una lista de ScrapedItem a diccionarios planos."""
        flat_list = []
        for it in items:
            row = dict(it.data)
            row["_source_url"] = it.source_url
            row["_timestamp"] = it.timestamp
            flat_list.append(row)
        return flat_list
