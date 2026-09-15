"""
UltraScrape - Exportador CSV
"""
import csv
import os
from typing import List
from core.models import ScrapedItem
from .base import BaseExporter


class CsvExporter(BaseExporter):
    def export(self, items: List[ScrapedItem]) -> bool:
        if not items:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        data = self.items_to_dict_list(items)

        # Obtener todos los campos presentes en los datos
        fieldnames = []
        for row in data:
            for k in row.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(self.output_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)

        return True
