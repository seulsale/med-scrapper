# Descargador de PDFs de Guías Clínicas IMSS

Un scraper en Python que descarga PDFs de guías de práctica clínica del Instituto Mexicano del Seguro Social (IMSS).

## Descripción General

Esta herramienta descarga automáticamente todos los PDFs GER (Guía de Evidencias y Recomendaciones) del sitio web de guías de práctica clínica del IMSS. Excluye los PDFs GRR (Guía de Referencia Rápida) para enfocarse en las guías clínicas integrales.

## Características

- **Descubrimiento Automático de PDFs**: Rastrea todas las páginas del sitio web de guías del IMSS
- **Descarga Selectiva**: Solo descarga PDFs GER (guías integrales)
- **Prevención de Duplicados**: Omite archivos que ya existen localmente
- **Manejo Robusto de Errores**: Incluye lógica de reintentos con retroceso exponencial
- **Seguimiento de Progreso**: Registro detallado del progreso y estado de descarga
- **Validación de Archivos**: Verifica el contenido PDF antes de guardar
- **Scraping Respetuoso**: Demoras integradas para evitar sobrecargar el servidor

## Requisitos

- Python 3.13+
- Dependencias: `requests`, `beautifulsoup4`, `lxml`

## Instalación

1. Clona el repositorio:
```bash
git clone <repository-url>
cd medicine-mx-scrapping
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

o usando uv:
```bash
uv sync
```

## Uso

Ejecuta el descargador:
```bash
python imss_pdf_downloader.py
```

El script:
1. Escanea todas las páginas del sitio web de guías clínicas del IMSS
2. Extrae enlaces PDF para documentos GER
3. Descarga PDFs al directorio `imss_pdfs/`
4. Registra el progreso tanto en consola como en `imss_download.log`

## Salida

- **PDFs Descargados**: Almacenados en el directorio `imss_pdfs/`
- **Convención de Nomenclatura**: Los archivos tienen prefijo con identificador IMSS cuando está disponible (ej. `IMSS-050-18_050GER.pdf`)
- **Archivo de Log**: `imss_download.log` contiene registros detallados de ejecución

## Detalles Técnicos

- **URL Base**: https://www.imss.gob.mx/guias_practicaclinica
- **Documentos Objetivo**: PDFs GER (guías clínicas integrales)
- **User Agent**: Simula un navegador web estándar para evitar bloqueos
- **Estrategia de Descarga**: Secuencial con demoras respetuosas entre solicitudes

## Estructura del Proyecto

```
medicine-mx-scrapping/
│   README.md
│   imss_pdf_downloader.py    # Script principal de scraping
│   pyproject.toml            # Configuración del proyecto
│   requirements.txt          # Dependencias de Python
│   uv.lock                   # Archivo de bloqueo UV
│   imss_download.log         # Log de ejecución
└── imss_pdfs/               # Directorio de PDFs descargados
```

## Consideraciones Éticas

Esta herramienta está diseñada para propósitos legítimos de investigación y educación. La herramienta:
- Respeta el sitio web del IMSS con demoras apropiadas entre solicitudes
- Solo descarga guías clínicas disponibles públicamente
- Incluye manejo adecuado de errores para evitar sobrecargar el servidor
- Utiliza una cadena de user agent respetuosa

Por favor, asegúrate de cumplir con los términos de servicio del IMSS y las leyes aplicables al usar esta herramienta.