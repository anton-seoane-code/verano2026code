# Directory Analyzer

CLI and Web GUI tool that analyzes a directory, classifies files by type (images, videos, documents), detects duplicates, and organizes them into subdirectories automatically.

## Requisitos

- Python 3.8+

## Instalación

```bash
git clone <repo>
cd directory-analyzer
```

## CLI Usage

```bash
python analyzer.py /ruta/al/directorio
```

### CLI Flags

| Flag | Descripción |
|------|-------------|
| `directory` | Ruta al directorio a analizar (requerido) |
| `--dry-run` | Vista previa sin mover ni copiar archivos |
| `--copy` | Copiar archivos en lugar de moverlos |
| `--recursive` | Escanear subdirectorios de forma recursiva |
| `--detect-duplicates` | Detectar archivos duplicados por hash SHA256 |
| `--analyze-only` | Solo analizar, no organizar |

### CLI Examples

```bash
# Analyze only (no file changes)
python analyzer.py ~/Descargas --recursive --detect-duplicates --analyze-only

# Organize files (move)
python analyzer.py ~/Descargas --recursive

# Preview before organizing
python analyzer.py ~/Descargas --dry-run --recursive
```

## Web GUI

```bash
python server.py
```

Opens at `http://localhost:8080`. The GUI includes:

- **Tree browser** — navigate and select directories interactively
- **Analysis** — scan, classify, detect duplicates (no file changes)
- **Organization** — move or copy files into `images/`, `videos/`, `documents/`
- **Report** — detailed text report with categories, duplicates, and results

### Extension Classification

| Categoría | Extensiones |
|-----------|-------------|
| Imágenes | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`, `.tiff`, `.tif` |
| Videos | `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v` |
| Documentos | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.txt`, `.csv`, `.md`, `.json`, `.xml`, `.html`, `.htm`, `.epub` |

Los subdirectorios se crean automáticamente (`images/`, `videos/`, `documents/`). Archivos ya dentro de subdirectorios se omiten.

## Duplicate Detection

La detección de duplicados agrupa archivos por tamaño y luego computa un hash SHA256 para confirmar duplicados exactos. Los grupos duplicados se muestran en el reporte y en la tabla de resultados del GUI.

## API

The web server exposes a JSON API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/browse` | POST | List directory contents for tree navigation |
| `/api/analyze` | POST | Scan and classify files, detect duplicates |
| `/api/organize` | POST | Move or copy files into categorized subdirectories |
