# ⚡ UltraScrape Studio

Suite profesional y modular de Web Scraping visual y dinámico construida con Python y PySide6.

Ubicación del proyecto: `C:\Users\alexander\Desktop\UltraScrape`

---

## 🌟 Características Principales (10/10)

1. **🌐 Entrada del Sitio Flexible**:
   - URL inicial directa.
   - Soporte para múltiples URLs (lista manual o carga masiva desde archivos `.txt` o `.csv`).
   - Configuración de `User-Agent` personalizado, encabezados HTTP (`Headers`) y cookies de sesión para sitios que requieran autenticación.

2. **🔎 Qué Datos Extraer**:
   - Soporte para selectores **CSS** y **XPath**.
   - Selector opcional de contenedor para extracción por bloques (ej. `.product-card`).
   - Modal interactivo para agregar, editar y probar selectores en vivo.
   - Extracción de texto, atributos HTML (`href`, `src`, `title`, `alt`, etc.) y filtrado con expresiones regulares (`Regex`).

3. **⚙️ Scraping Dinámico (Playwright)**:
   - Renderizado completo de páginas dinámicas con **JavaScript**.
   - Modo **Headless** o ventana visual del navegador.
   - **Scroll infinito** automático configurable con límites de scroll y retrasos.
   - Manejo de botones de carga dinámica (**"Load more"**).
   - Espera interactiva de selectores específicos antes de extraer (`wait_for_selector`).

4. **🧹 Procesamiento y Normalización de Datos**:
   - **Eliminación de duplicados**: Mediante hash criptográfico SHA-256 o clave específica.
   - **Limpieza de espacios**: Eliminación de saltos de línea superfluos y espacios múltiples.
   - **Normalización de precios**: Extracción automática de números de texto como `"$ 1,299.99 MXN"` o `"1.450,50 €"`.
   - **Normalización de fechas**: Conversión de formatos y fechas relativas ("hoy", "ayer", "hace 2 días") a estándar ISO `AAAA-MM-DD`.
   - **Validación de URLs**: Conversión de rutas relativas a absolutas y comprobación de protocolo.
   - **Filtro de incompletos**: Descarte automático de filas vacías o sin campos obligatorios.

5. **📦 Exportación Multiformato**:
   - **CSV**: Con codificación `UTF-8-sig` (compatible directamente con Microsoft Excel).
   - **Excel (.xlsx)**: Con cabeceras estilizadas y auto-ajuste de ancho de columnas.
   - **JSON**: Con formato legible e identado o formato de líneas (JSONL).
   - **SQLite**: Creación automática de tablas relacionales e índices.

6. **📊 Vista Previa en Tiempo Real**:
   - Tabla interactiva que se actualiza fila por fila a medida que se extrae.
   - Buscador / filtro instantáneo sobre los resultados obtenidos.
   - Menú contextual: Copiar celda o fila completa al portapapeles.
   - Botón de exportación rápida sin detener el flujo de trabajo.

7. **🚀 Control del Scraping y Métricas**:
   - Métricas en vivo: Número de páginas, registros encontrados, errores y velocidad (`pág/s`).
   - Barra de progreso visual interactiva.
   - Control de ejecución: **[ ▶ INICIAR ]**, **[ ⏸️ PAUSAR ] / [ ▶️ REANUDAR ]**, **[ 🛑 DETENER ]**.
   - Concurrencia, límites de páginas y registros, delay entre solicitudes y reintentos automáticos.

8. **💾 Gestión de Proyectos**:
   - Estructura organizada por carpetas:
     ```
     projects/
     ├── demo_ecommerce/
     │   ├── config.json
     │   └── results/
     ```
   - Guardar, abrir, duplicar y eliminar proyectos con un clic.

9. **🖥️ GUI Moderna (PySide6)**:
   - Tema oscuro estilo Cyber-Dark con alto contraste y ergonomía visual.
   - Arquitectura desacoplada: El motor de scraping corre en un `QThread` independiente, garantizando que la interfaz jamás se congele.

10. **🔬 Constructor y Probador en Vivo de Selectores**:
    - Prueba cualquier selector CSS o XPath contra la URL objetivo y visualiza las primeras 10 coincidencias antes de iniciar un scraping masivo.

---

## 🚀 Cómo Iniciar

### 1. Instalación Rápida
Haz doble clic en:
```
install_dependencies.bat
```
O desde la terminal:
```bash
python -m pip install -r requirements.txt
python -m playwright install
```

### 2. Ejecutar la Aplicación Gráfica
Haz doble clic en:
```
run_app.bat
```
O ejecuta:
```bash
python main.py
```

### 3. Modo CLI / Headless (Sin GUI)
Para ejecutar directamente desde consola usando un proyecto guardado:
```bash
python main.py --cli --project projects/demo_ecommerce/config.json
```

### 4. Autodiagnóstico del Sistema
Para comprobar que todos los componentes (modelos, extractor, procesador y exportadores) funcionan al 100%:
```bash
python main.py --test
```

---

## 📁 Estructura del Código

```
UltraScrape/
├── core/
│   ├── models.py           # Modelos de datos y configuraciones
│   ├── extractor.py        # Motor de extracción CSS/XPath
│   ├── processor.py        # Pipeline de limpieza y deduplicación
│   ├── pagination.py       # Paginación y navegación
│   ├── browser.py          # Playwright y renderizado dinámico
│   └── crawler.py          # Orquestador del scraping
├── exporters/
│   ├── base.py             # Clase base de exportadores
│   ├── csv_exporter.py     # Exportador CSV
│   ├── excel_exporter.py   # Exportador XLSX
│   ├── json_exporter.py    # Exportador JSON
│   └── sqlite_exporter.py  # Exportador SQLite
├── gui/
│   ├── styles.py           # Estilos QSS Cyber-Dark
│   ├── worker.py           # QThread con señales Qt
│   ├── selector_dialog.py  # Modal probador de selectores
│   ├── results_widget.py   # Tabla de resultados en tiempo real
│   ├── project_manager.py  # Gestor de proyectos
│   └── main_window.py      # Ventana principal
├── projects/
│   └── demo_ecommerce/     # Proyecto de prueba funcional
├── install_dependencies.bat
├── run_app.bat
├── requirements.txt
└── main.py
```
