"""
UltraScrape - Exportador SQLite
"""
import sqlite3
import os
import re
from typing import List
from core.models import ScrapedItem
from .base import BaseExporter


class SqliteExporter(BaseExporter):
    def __init__(self, output_path: str, table_name: str = "scraped_data"):
        super().__init__(output_path)
        # Sanitizar nombre de tabla
        self.table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name) or "scraped_data"

    def export(self, items: List[ScrapedItem]) -> bool:
        if not items:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        data = self.items_to_dict_list(items)

        # Detectar columnas
        columns = []
        for row in data:
            for k in row.keys():
                col_clean = re.sub(r'[^a-zA-Z0-9_]', '_', k)
                if col_clean not in columns:
                    columns.append(col_clean)

        conn = sqlite3.connect(self.output_path)
        cursor = conn.cursor()

        try:
            # Crear tabla dinámicamente
            col_definitions = [f'"{col}" TEXT' for col in columns]
            create_query = f'''
                CREATE TABLE IF NOT EXISTS "{self.table_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {", ".join(col_definitions)}
                )
            '''
            cursor.execute(create_query)

            # Insertar registros
            placeholders = ", ".join(["?"] * len(columns))
            quoted_cols = ", ".join([f'"{c}"' for c in columns])
            insert_query = f'INSERT INTO "{self.table_name}" ({quoted_cols}) VALUES ({placeholders})'

            rows_to_insert = []
            for item_dict in data:
                row_vals = []
                for col in columns:
                    val = item_dict.get(col, "")
                    row_vals.append(str(val) if val is not None else "")
                rows_to_insert.append(row_vals)

            cursor.executemany(insert_query, rows_to_insert)
            conn.commit()
            return True
        finally:
            conn.close()
