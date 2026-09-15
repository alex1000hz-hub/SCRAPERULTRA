"""
UltraScrape - Exportador JSON / JSONL
"""
import json
import os
from typing import List
from core.models import ScrapedItem
from .base import BaseExporter


class JsonExporter(BaseExporter):
    def __init__(self, output_path: str, lines: bool = False):
        super().__init__(output_path)
        self.lines = lines

    def export(self, items: List[ScrapedItem]) -> bool:
        if not items:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        data = self.items_to_dict_list(items)

        with open(self.output_path, "w", encoding="utf-8") as f:
            if self.lines:
                for row in data:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return True
