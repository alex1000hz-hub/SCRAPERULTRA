# 📖 MANUAL DE INSTRUCCIONES Y GUÍA DE USO - ULTRASCRAPE STUDIO

Bienvenido a la guía completa de **UltraScrape Studio**. Este documento detalla minuciosamente el funcionamiento de **cada sector, panel y botón** de la suite, así como tutoriales paso a paso para extraer datos de cualquier página web.

---

## 📑 ÍNDICE
1. [Arquitectura Visual de la Pantalla](#1-arquitectura-visual-de-la-pantalla)
2. [Sector Superior: Gestión de Proyectos](#2-sector-superior-gestión-de-proyectos)
3. [Sector 1: Entrada del Sitio (URLs, Headers y Cookies)](#3-sector-1-entrada-del-sitio-urls-headers-y-cookies)
4. [Sector 2: Qué Datos Extraer (Selectores CSS, XPath y Atributos)](#4-sector-2-qué-datos-extraer-selectores-css-xpath-y-atributos)
5. [Sector 3: Scraping Dinámico (Playwright y JavaScript)](#5-sector-3-scraping-dinámico-playwright-y-javascript)
6. [Sector 4: Paginación Automática](#6-sector-4-paginación-automática)
7. [Sector 5: Procesamiento y Limpieza de Datos](#7-sector-5-procesamiento-y-limpieza-de-datos)
8. [Sector 6: Control de Velocidad y Red (Anti-Baneo)](#8-sector-6-control-de-velocidad-y-red-anti-baneo)
9. [Sector 7: Exportación de Resultados](#9-sector-7-exportación-de-resultados)
10. [Sector 8: Barra de Control y Progreso](#10-sector-8-barra-de-control-y-progreso)
11. [Sector 9: Vista Previa en Vivo y Consola de Eventos](#11-sector-9-vista-previa-en-vivo-y-consola-de-eventos)
12. [Tutorial Paso a Paso: Cómo scrapear cualquier web desde cero](#12-tutorial-paso-a-paso-cómo-scrapear-cualquier-web-desde-cero)

---

## 1. Arquitectura Visual de la Pantalla

La aplicación se divide en dos grandes paneles:
- **Panel Izquierdo (Configuración y Acciones)**: Dividido en 4 pestañas organizadas lógicamente (`🎯 Extracción`, `⚡ Dinámico & Páginas`, `🧹 Limpieza & Red`, `📦 Exportación`) y la botonera de ejecución (`▶ INICIAR`, `⏸️ PAUSAR`, `🛑 DETENER`).
- **Panel Derecho (Resultados y Monitoreo)**: Contiene la **Vista Previa de Datos** (tabla interactiva en tiempo real) y la **Consola de Eventos** (logs del sistema).

---

## 2. Sector Superior: Gestión de Proyectos

En la parte superior encontrarás:
- **Nombre del Proyecto**: Campo de texto para nombrar tu proyecto (ej: `amazon_ofertas`, `inmobiliaria_casas`, `google_news`).
- **Botón `📄 Nuevo`**: Limpia todas las configuraciones actuales para empezar un proyecto desde cero.
- **Botón `📂 Abrir`**: Abre la ventana del Gestor de Proyectos donde puedes cargar o eliminar proyectos existentes guardados en tu carpeta `projects/`.
- **Botón `💾 Guardar`**: Guarda todos los selectores, URLs, opciones de red y formatos de exportación en `projects/<nombre>/config.json`. Al abrirlo en el futuro, todo se restaurará automáticamente.

---

## 3. Sector 1: Entrada del Sitio (URLs, Headers y Cookies)

Aquí defines a qué páginas se conectará el scraper:

1. **Campo `URL Inicial`**:
   - Ingresa la dirección principal donde iniciará la extracción (ejemplo: `https://ejemplo.com/tienda`).
2. **Cargar TXT/CSV (`📁 Cargar TXT/CSV`)**:
   - Si tienes un archivo con 500 URLs que quieres raspar una tras otra, pulsa este botón. El sistema las leerá y cargará en la cola.
3. **Múltiples URLs (Área de texto)**:
   - Puedes pegar una lista de URLs, una por cada renglón. El motor recorrerá cada una en orden.
4. **Botón `⚙️ Headers & Cookies de Sesión`**:
   - **User-Agent**: La firma con la que te identificas ante el servidor web (por defecto viene configurado como Chrome de última generación para evitar que te confundan con un bot simple).
   - **Headers Adicionales**: Encabezados HTTP (ej: `Referer`, `Authorization: Bearer token...`, etc.).
   - **Cookies**: Cookies de sesión en formato `nombre=valor; nombre2=valor2`. Esencial cuando quieres scrapear sitios protegidos por login donde ya tienes tu cuenta de usuario abierta.

---

## 4. Sector 2: Qué Datos Extraer (Selectores CSS, XPath y Atributos)

Este es el corazón del extractor. Aquí le dices a UltraScrape exactamente qué partes del código HTML debe guardar.

### El Campo "Contenedor (ej. `.product-card`)"
- **¿Para qué sirve?**: Si estás raspando un catálogo con 20 productos por página, no quieres que los títulos y los precios se desordenen. Al poner el selector de la tarjeta o fila (ejemplo: `.product-card`, `div.articulo`, `tr.fila`), UltraScrape extraerá los campos **en bloque para cada producto individual**.
- Si lo dejas vacío, UltraScrape extraerá los elementos a nivel general de página y los alineará automáticamente.

### Tabla de Selectores
Muestra las columnas que extraerás:
- **Campo**: El nombre de la columna que verás en tu Excel/CSV (ej: `titulo`, `precio`, `imagen`, `enlace`).
- **Selector**: La ruta CSS o XPath que apunta al elemento (ej: `.product-title`, `//span[@class='precio']`).
- **Tipo**: Si la consulta está en formato `CSS` o `XPath`.
- **Atributo**:
  - `text` o `innertext`: Extrae el texto visible del elemento.
  - `href`: Extrae el link o enlace a donde lleva (UltraScrape lo convierte automáticamente a URL completa `https://...`).
  - `src`: Extrae la dirección URL de una foto o imagen.
  - `html`: Extrae el código HTML interno si necesitas etiquetas crudas.
  - Otros: Cualquier atributo como `data-id`, `alt`, `title`, etc.

### Ventana "Constructor y Probador en Vivo" (`➕ Agregar Selector`)
Al presionar **`➕ Agregar Selector`** o **`✏️ Editar`**, se abre el asistente:
- **Filtro Regex (Opcional)**: Permite extraer solo una parte del texto con expresiones regulares. Ejemplo: `\d+(\.\d+)?` para extraer únicamente los dígitos.
- **Obligatorio**: Si marcas esta casilla, cuando una página no tenga este campo (por ejemplo, un producto sin precio o sin stock), ese registro será descartado para evitar filas incompletas.
- **Probador en Vivo (Instant Preview)**:
  - Ingresas la URL de prueba.
  - Presionas **`🔍 Probar Selector`**.
  - UltraScrape se conecta a la web, evalúa el selector y te muestra en un recuadro las **primeras 10 coincidencias reales** encontradas en tiempo real. ¡Así nunca empezarás un scraping a ciegas!

---

## 5. Sector 3: Scraping Dinámico (Playwright y JavaScript)

Ubicado en la pestaña **`⚡ Dinámico & Páginas`**:
- **☑ Habilitar JavaScript y navegador dinámico**: Utiliza Playwright Chromium para sitios web modernos (React, Vue, Angular) que no muestran el contenido hasta que se ejecuta el código JavaScript.
- **☐ Modo Headless**:
  - *Marcado*: El navegador trabaja en segundo plano sin ventana (más rápido y consume menos memoria).
  - *Desmarcado*: Se abre una ventana visible de Google Chrome para que veas con tus propios ojos cómo se navega y se cargan las páginas.
- **☑ Scroll infinito automático**:
  - Para sitios como Twitter, Instagram, TikTok o tiendas que cargan más productos según bajas con la rueda del ratón.
  - Puedes configurar el **Límite de scrolls** (cuántas veces bajará) y la **Espera en segundos** entre scroll y scroll para dar tiempo a que los nuevos datos carguen.
- **Botón 'Load More'**:
  - Si la página tiene un botón "Cargar más productos", ingresas su selector CSS aquí y UltraScrape le hará clic de forma automática.
- **Esperar selector**:
  - Espera hasta que aparezca un elemento clave (ejemplo: `.catalogo-cargado`) antes de empezar a extraer, evitando capturar pantallas en blanco.

---

## 6. Sector 4: Paginación Automática

Para recorrer catálogos de 2, 10 o 50 páginas seguidas:
- **Botón Siguiente (Next Button)**:
  - Ingresas el selector del botón o flecha de siguiente página (ej: `a.next`, `li.pagination-next a`). UltraScrape lo detecta, extrae el enlace y continúa navegando automáticamente.
- **Patrón de URL (?page={page})**:
  - Si las páginas siguen un formato predecible, ingresas una plantilla como:
    `https://tienda.com/productos?page={page}`
  - UltraScrape sustituirá `{page}` por `1, 2, 3...` hasta el número que hayas fijado en **Máximo de páginas**.

---

## 7. Sector 5: Procesamiento y Limpieza de Datos

Ubicado en la pestaña **`🧹 Limpieza & Red`**. Los datos no solo se extraen, sino que se normalizan antes de guardarse:
- **☑ Eliminar registros duplicados**: Calcula un hash SHA-256 único de cada fila para evitar registros repetidos.
- **☑ Limpiar espacios en blanco**: Elimina dobles espacios, tabuladores y saltos de línea invisibles.
- **☑ Normalizar precios a formato numérico**:
  - Convierte textos como `"$ 1,299.99 MXN"` o `"1.450,50 €"` directamente en números decimales limpios (`1299.99` o `1450.50`), listos para operaciones matemáticas.
- **☑ Convertir fechas**:
  - Detecta formatos relativos ("hace 2 horas", "hoy", "ayer") y formatos internacionales para convertirlos a formato estándar ISO `AAAA-MM-DD`.
- **☑ Validar URLs**:
  - Detecta links relativos como `/producto/1` y los convierte en absolutos (`https://tienda.com/producto/1`).
- **☑ Eliminar registros incompletos**:
  - Descarta filas vacías o que carezcan de los datos clave.

---

## 8. Sector 6: Control de Velocidad y Red (Anti-Baneo)

Para evitar que los servidores te bloqueen o te muestren un CAPTCHA:
- **Delay entre solicitudes (segundos)**: Pausa entre cada página descargada (ej: `1.0` o `2.0` segundos).
- **Límite de registros**: Se detiene automáticamente cuando alcanza el número fijado (ej: 500 productos). Si pones `0`, raspará todo sin límite.
- **Timeout por petición**: Tiempo máximo que esperará antes de considerar que una página no responde.
- **Reintentos por error**: Si la conexión falla, reintentará hasta 3 veces automáticamente antes de reportar un error.

---

## 9. Sector 7: Exportación de Resultados

En la pestaña **`📦 Exportación`**:
- **Formato de Salida**:
  - **CSV**: Con codificación `UTF-8-sig`. Ideal para abrir directamente en Microsoft Excel sin problemas de tildes o caracteres especiales.
  - **Excel (.xlsx)**: Hoja de cálculo con encabezados oscuros, fuentes legibles y ancho de columnas auto-ajustado.
  - **JSON**: Formato legible estructurado para desarrolladores o bases de datos NoSQL.
  - **SQLite (.db)**: Crea una base de datos relacional y sus tablas automáticamente.
- **Archivo Destino**: Puedes elegir el nombre y la ruta de guardado mediante el botón `📁 Examinar...`.

---

## 10. Sector 8: Barra de Control y Progreso

Ubicada en la parte inferior del panel izquierdo:
- **`▶ INICIAR`**: Comienza el proceso de extracción en un subproceso independiente.
- **`⏸️ PAUSAR` / `▶️ REANUDAR`**: Detiene momentáneamente la descarga en curso sin perder los datos ya acumulados.
- **`🛑 DETENER`**: Detiene de forma segura el proceso y consolida los resultados obtenidos hasta ese momento.
- **Barra de Progreso y Estadísticas**:
  - Muestra el porcentaje de avance, cantidad de registros obtenidos y la velocidad de trabajo en **páginas por segundo (`pág/s`)**.

---

## 11. Sector 9: Vista Previa en Vivo y Consola de Eventos

Ubicado en el panel derecho:

### Pestaña `📊 Vista Previa de Datos`
- **Tabla en Tiempo Real**: Cada producto o noticia que se extrae aparece de inmediato en la tabla.
- **Buscador instantáneo**: Escribe cualquier palabra en el campo `🔍 Filtrar en resultados...` y la tabla ocultará al instante las filas que no coincidan.
- **Menú contextual**: Haz clic derecho sobre cualquier celda para copiar su texto o la fila completa al portapapeles.
- **Botón `💾 Exportar Rápido`**: Permite guardar en cualquier momento los datos visibles sin tener que esperar a que el proceso termine.

### Pestaña `📋 Consola de Eventos`
- Muestra el registro técnico de la operación: URLs descargadas, reintentos de red, códigos de respuesta, tiempos de respuesta y advertencias del sistema.

---

## 12. Tutorial Paso a Paso: Cómo scrapear cualquier web desde cero

Sigue estos sencillos pasos para extraer información de cualquier sitio web:

### Paso 1: Obtener el selector en tu navegador
1. Abre la página web en Google Chrome o Edge (ej: una tienda o portal de noticias).
2. Haz clic derecho sobre el texto que quieres extraer (ejemplo: el título de un producto) y selecciona **"Inspeccionar"**.
3. En el panel de código que se abre, verás la etiqueta HTML resaltada.
4. Haz clic derecho sobre la etiqueta resaltada -> **Copiar** -> **Copiar selector** (o Copiar XPath).

### Paso 2: Configurar en UltraScrape
1. Abre **UltraScrape** (doble clic en `run_app.bat`).
2. En **URL Inicial**, pega la dirección de la página.
3. Haz clic en **`➕ Agregar Selector`**:
   - **Nombre**: Ponle un nombre descriptivo (ej: `titulo`).
   - **Selector**: Pega el selector que copiaste en el paso 1.
   - **Atributo**: Déjalo en `text` para texto, o cámbialo a `href` si es un enlace, o a `src` si es una foto.
   - Haz clic en **`🔍 Probar Selector`** para verificar que devuelva los datos correctos.
   - Haz clic en **`Guardar Selector`**.
4. Repite el proceso para los demás campos que quieras (ej: `precio`, `descripcion`, `imagen`).

### Paso 3: Ejecutar y Exportar
1. Haz clic en el botón verde **`▶ INICIAR`**.
2. Verás cómo los datos van apareciendo en la tabla.
3. Cuando termine, haz clic en **`💾 Exportar Rápido`** o revisa el archivo generado automáticamente en la carpeta del proyecto.
