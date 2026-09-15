"""
UltraScrape - Pipeline de Normalización, Limpieza y Validación de Datos
"""
import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse
from datetime import datetime, timedelta

from .models import ProcessorConfig, ScrapedItem


class DataProcessor:
    def __init__(self, config: Optional[ProcessorConfig] = None):
        self.config = config or ProcessorConfig()
        self.seen_hashes: Set[str] = set()
        self.seen_keys: Set[str] = set()

    def reset_state(self) -> None:
        """Reinicia el historial de deduplicación."""
        self.seen_hashes.clear()
        self.seen_keys.clear()

    @staticmethod
    def clean_spaces(text: Any) -> Any:
        """Limpia saltos de línea excesivos y múltiples espacios consecutivos."""
        if not isinstance(text, str):
            return text
        # Reemplazar caracteres invisibles y saltos por espacio
        cleaned = re.sub(r'[\r\n\t]+', ' ', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    @staticmethod
    def normalize_price(val: Any) -> Any:
        """
        Extrae y normaliza valores monetarios.
        Ejemplos:
          '$ 1,299.99 MXN' -> 1299.99
          '1.450,50 €'    -> 1450.50
          'Gratis'        -> 0.0
        """
        if isinstance(val, (int, float)):
            return float(val)
        if not isinstance(val, str):
            return val

        text = val.strip().lower()
        if "gratis" in text or "free" in text:
            return 0.0

        # Buscar dígitos con posibles separadores
        match = re.search(r'([\d.,\s]+)', text)
        if not match:
            return val

        raw_num = match.group(1).strip()
        # Caso: formato europeo con comas como decimales ej: 1.250,50
        if ',' in raw_num and '.' in raw_num:
            if raw_num.rfind(',') > raw_num.rfind('.'):
                # Punto es separador de miles, coma es decimal
                clean_num = raw_num.replace('.', '').replace(',', '.')
            else:
                # Coma es miles, punto es decimal
                clean_num = raw_num.replace(',', '')
        elif ',' in raw_num:
            # Si solo tiene comas, verificar si es decimal o miles
            parts = raw_num.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                clean_num = raw_num.replace(',', '.')
            else:
                clean_num = raw_num.replace(',', '')
        else:
            clean_num = raw_num.replace(' ', '')

        try:
            return float(clean_num)
        except ValueError:
            return val

    @staticmethod
    def normalize_date(val: Any) -> Any:
        """Normaliza fechas comunes en español/inglés a formato ISO AAAA-MM-DD."""
        if not isinstance(val, str) or not val.strip():
            return val

        text = val.strip().lower()
        now = datetime.now()

        # Detección de fechas relativas
        if "hoy" in text or "today" in text:
            return now.strftime("%Y-%m-%d")
        if "ayer" in text or "yesterday" in text:
            return (now - timedelta(days=1)).strftime("%Y-%m-%d")

        m_hours = re.search(r'hace\s+(\d+)\s+hora', text)
        if m_hours:
            return (now - timedelta(hours=int(m_hours.group(1)))).strftime("%Y-%m-%d %H:%M")

        m_days = re.search(r'hace\s+(\d+)\s+d[íi]a', text)
        if m_days:
            return (now - timedelta(days=int(m_days.group(1)))).strftime("%Y-%m-%d")

        # Patrones comunes AAAA-MM-DD o DD/MM/AAAA
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return val

    @staticmethod
    def is_valid_url(url: Any) -> bool:
        """Verifica si la cadena es una URL HTTP/HTTPS válida."""
        if not isinstance(url, str):
            return False
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)

    def compute_record_hash(self, record: Dict[str, Any]) -> str:
        """Genera un hash SHA256 para identificar duplicados."""
        sorted_items = sorted((str(k), str(v)) for k, v in record.items())
        serialized = "||".join(f"{k}:{v}" for k, v in sorted_items)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def is_duplicate(self, record: Dict[str, Any]) -> bool:
        """Determina si un registro ya fue procesado."""
        if not self.config.deduplicate:
            return False

        if self.config.deduplicate_by and self.config.deduplicate_by in record:
            key_val = str(record[self.config.deduplicate_by]).strip()
            if not key_val:
                return False
            if key_val in self.seen_keys:
                return True
            self.seen_keys.add(key_val)
            return False
        else:
            rec_hash = self.compute_record_hash(record)
            if rec_hash in self.seen_hashes:
                return True
            self.seen_hashes.add(rec_hash)
            return False

    def is_incomplete(self, record: Dict[str, Any]) -> bool:
        """Verifica si al registro le faltan campos obligatorios o está vacío."""
        if not record:
            return True

        if self.config.drop_incomplete:
            # Si se especificaron campos obligatorios
            if self.config.required_fields:
                for req in self.config.required_fields:
                    val = record.get(req)
                    if val is None or str(val).strip() == "":
                        return True
            else:
                # Si todos los campos están vacíos
                all_empty = all(v is None or str(v).strip() == "" for v in record.values())
                if all_empty:
                    return True

        return False

    def process_record(self, record: Dict[str, Any], source_url: str = "", page_number: int = 1) -> Optional[ScrapedItem]:
        """
        Ejecuta el pipeline completo de limpieza, normalización y validación sobre un registro.
        Retorna None si debe ser descartado (por duplicado o incompleto).
        """
        processed: Dict[str, Any] = {}

        for key, value in record.items():
            current_val = value

            # 1. Limpieza de espacios
            if self.config.trim_spaces and isinstance(current_val, str):
                current_val = self.clean_spaces(current_val)

            # 2. Normalización de precios (si el nombre del campo sugiere precio)
            if self.config.normalize_prices and any(w in key.lower() for w in ("precio", "price", "cost", "costo", "monto")):
                current_val = self.normalize_price(current_val)

            # 3. Normalización de fechas
            if self.config.convert_dates and any(w in key.lower() for w in ("fecha", "date", "tiempo", "time")):
                current_val = self.normalize_date(current_val)

            # 4. Validación de URL
            if self.config.validate_urls and any(w in key.lower() for w in ("url", "link", "enlace", "imagen", "image", "img")):
                if isinstance(current_val, str) and current_val and not self.is_valid_url(current_val):
                    # Si no es válida, la marcamos o intentamos mantenerla
                    pass

            processed[key] = current_val

        # Filtrar incompletos
        if self.is_incomplete(processed):
            return None

        # Filtrar duplicados
        if self.is_duplicate(processed):
            return None

        return ScrapedItem(
            data=processed,
            source_url=source_url,
            page_number=page_number,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
