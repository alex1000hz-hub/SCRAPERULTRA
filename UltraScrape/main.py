"""
UltraScrape - Punto de Entrada Principal (GUI & CLI)
"""
import sys
import os
import argparse

# Configurar salida de consola segura para Windows UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Cargar variables de entorno si python-dotenv está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.models import ProjectConfig, ScrapedItem, ScrapeStats
from core.crawler import ScraperEngine


def run_self_test():
    """Ejecuta una prueba automática de verificación de componentes del sistema."""
    print("=" * 60)
    print("⚡ ULTRASCRAPE - VERIFICACIÓN DE COMPONENTES")
    print("=" * 60)

    # 1. Test Modelos
    print("[1/5] Verificando modelos y serialización...", end=" ")
    cfg = ProjectConfig(name="SelfTest")
    data_dict = cfg.to_dict()
    assert data_dict["name"] == "SelfTest"
    print("✅ OK")

    # 2. Test Extractor
    print("[2/5] Verificando motor de extracción...", end=" ")
    from core.extractor import Extractor, SelectorConfig
    extractor = Extractor("https://example.com")
    html_sample = """
    <html>
        <body>
            <div class="card">
                <h2 class="title">Teclado Mecánico RGB</h2>
                <span class="price">$ 1,499.50 MXN</span>
                <a href="/producto/123" class="link">Ver</a>
            </div>
            <div class="card">
                <h2 class="title">Mouse Inalámbrico Pro</h2>
                <span class="price">$ 750.00 MXN</span>
                <a href="/producto/456" class="link">Ver</a>
            </div>
        </body>
    </html>
    """
    selectors = [
        SelectorConfig(name="producto", selector=".title", selector_type="css", attribute="text"),
        SelectorConfig(name="precio", selector=".price", selector_type="css", attribute="text"),
        SelectorConfig(name="enlace", selector=".link", selector_type="css", attribute="href")
    ]
    extracted = extractor.extract_items_from_containers(html_sample, ".card", selectors, "https://example.com")
    assert len(extracted) == 2
    assert extracted[0]["producto"] == "Teclado Mecánico RGB"
    assert extracted[0]["enlace"] == "https://example.com/producto/123"
    print("✅ OK (2 items extraídos y enlaces resueltos)")

    # 3. Test Procesador
    print("[3/5] Verificando pipeline de normalización y limpieza...", end=" ")
    from core.processor import DataProcessor, ProcessorConfig
    proc = DataProcessor(ProcessorConfig(deduplicate=True, normalize_prices=True, trim_spaces=True))
    item1 = proc.process_record(extracted[0], "https://example.com", 1)
    assert item1 is not None
    assert item1.data["precio"] == 1499.5  # Normalizado a float
    # Probar deduplicación
    item1_dup = proc.process_record(extracted[0], "https://example.com", 1)
    assert item1_dup is None  # Debe ser descartado por duplicado
    print("✅ OK (Precios normalizados y duplicados filtrados)")

    # 4. Test Exportadores
    print("[4/5] Verificando exportadores (CSV, JSON, SQLite)...", end=" ")
    from exporters.csv_exporter import CsvExporter
    from exporters.json_exporter import JsonExporter
    from exporters.sqlite_exporter import SqliteExporter

    test_export_dir = os.path.join(BASE_DIR, "projects", "selftest_export")
    os.makedirs(test_export_dir, exist_ok=True)

    csv_path = os.path.join(test_export_dir, "test.csv")
    json_path = os.path.join(test_export_dir, "test.json")
    db_path = os.path.join(test_export_dir, "test.db")

    item_sample = [item1]
    assert CsvExporter(csv_path).export(item_sample)
    assert JsonExporter(json_path).export(item_sample)
    assert SqliteExporter(db_path).export(item_sample)
    print("✅ OK (CSV, JSON, SQLite generados con éxito)")

    # Limpiar archivos de prueba
    import shutil
    shutil.rmtree(test_export_dir, ignore_errors=True)

    # 5. Test PySide6
    print("[5/5] Verificando entorno gráfico PySide6...", end=" ")
    try:
        import PySide6
        print(f"✅ OK (PySide6 versión {PySide6.__version__} detectada)")
    except ImportError:
        print("⚠️ PySide6 no está instalado en el entorno actual de Python.")
        print("   -> Para iniciar la GUI, ejecute: pip install PySide6")

    print("=" * 60)
    print("🎉 ¡TODAS LAS PRUEBAS DE ARQUITECTURA COMPLETADAS CON ÉXITO!")
    print("=" * 60)


def run_cli_scraper(config_path: str):
    """Ejecuta el scraper en modo consola/CLI."""
    if not os.path.exists(config_path):
        print(f"❌ Error: Archivo de configuración no encontrado en '{config_path}'")
        sys.exit(1)

    print(f"📖 Cargando configuración desde: {config_path}")
    project = ProjectConfig.load_from_file(config_path)

    engine = ScraperEngine(project)
    engine.on_log_message = lambda msg: print(f"[UltraScrape] {msg}")
    engine.on_item_scraped = lambda item: print(f"  👉 Extraído: {item.data}")
    engine.on_stats_changed = lambda stats: print(
        f"  📊 Páginas: {stats.pages_scraped} | Registros: {stats.records_found} | Vel: {stats.current_speed} p/s",
        end="\r"
    )

    print(f"🚀 Iniciando scraping para: {project.name}")
    engine.run()

    # Exportar si tiene ruta configurada
    if project.export.output_path and engine.scraped_items:
        out = os.path.join(BASE_DIR, project.export.output_path)
        fmt = project.export.format.lower()
        if fmt == "csv":
            from exporters.csv_exporter import CsvExporter
            CsvExporter(out).export(engine.scraped_items)
        elif fmt == "xlsx":
            from exporters.excel_exporter import ExcelExporter
            ExcelExporter(out).export(engine.scraped_items)
        elif fmt == "json":
            from exporters.json_exporter import JsonExporter
            JsonExporter(out).export(engine.scraped_items)
        elif fmt == "sqlite":
            from exporters.sqlite_exporter import SqliteExporter
            SqliteExporter(out).export(engine.scraped_items)
        print(f"\n📦 Archivo exportado en: {out}")


def run_gui():
    """Lanza la aplicación gráfica PySide6."""
    try:
        from PySide6.QtWidgets import QApplication
        from gui.main_window import MainWindow
    except ImportError:
        print("\n" + "=" * 65)
        print("❌ Error: PySide6 no está instalado en este entorno de Python.")
        print("Para instalarlo y abrir la interfaz gráfica ejecuta:")
        print("   python -m pip install PySide6")
        print("O haz doble clic en el archivo:")
        print("   install_dependencies.bat")
        print("=" * 65 + "\n")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("UltraScrape Studio")
    app.setOrganizationName("UltraScrape")

    projects_dir = os.path.join(BASE_DIR, "projects")
    window = MainWindow(projects_dir=projects_dir)
    window.show()

    sys.exit(app.exec())


def main():
    parser = argparse.ArgumentParser(description="UltraScrape - Suite Profesional de Web Scraping")
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo CLI sin interfaz gráfica")
    parser.add_argument("--project", type=str, default="", help="Ruta al config.json para modo CLI")
    parser.add_argument("--test", action="store_true", help="Ejecutar autoevaluación y verificación de componentes")
    args = parser.parse_args()

    if args.test:
        run_self_test()
    elif args.cli:
        proj_path = args.project or os.path.join(BASE_DIR, "projects", "demo_ecommerce", "config.json")
        run_cli_scraper(proj_path)
    else:
        run_gui()


if __name__ == "__main__":
    main()
