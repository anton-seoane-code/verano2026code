# Directory Analyzer

CLI tool that analyzes a directory, classifies files by type (images, videos, documents), and organizes them into subdirectories automatically.

## Requisitos

- Python 3.8+

## Instalación

```bash
git clone <repo>
cd directory-analyzer
```

## Uso

```bash
python analyzer.py /ruta/al/directorio
```

### Flags

| Flag | Descripción |
|------|-------------|
| `directory` | Ruta al directorio a analizar (requerido) |
| `--dry-run` | Vista previa sin mover ni copiar archivos |
| `--copy` | Copiar archivos en lugar de moverlos |
| `--recursive` | Escanear subdirectorios de forma recursiva |

### Ejemplo

```bash
python analyzer.py ~/Descargas --dry-run --recursive
```

Clasifica archivos en las siguientes extensiones:

| Categoría | Extensiones |
|-----------|-------------|
| Imágenes | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`, `.tiff`, `.tif` |
| Videos | `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v` |
| Documentos | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.txt`, `.csv`, `.md`, `.json`, `.xml`, `.html`, `.htm`, `.epub` |

Los subdirectorios se crean automáticamente (`images/`, `videos/`, `documents/`). Los archivos que ya están dentro de subdirectorios se omiten.
