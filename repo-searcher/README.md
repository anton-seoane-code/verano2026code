# repo-searcher

Busca repositorios en GitHub por palabra clave, mostrando nombre, estrellas, lenguaje y descripción. Incluye interfaz de línea de comandos (CLI) e interfaz gráfica (GUI).

## Requisitos

- Python 3.8+

## Instalación

```bash
pip install -r requirements.txt
```

## Uso (CLI)

```bash
python repo_searcher.py "machine learning"
python repo_searcher.py "web framework" --limit 20
python repo_searcher.py rust --language rust --min-stars 5000
python repo_searcher.py "data science" --language python -s 1000 -l 15
```

### Flags

| Flag | Descripción |
|------|-------------|
| `keyword` | Palabra clave a buscar (obligatorio) |
| `-l`, `--limit` | Número máximo de resultados (1-100, defecto: 10) |
| `--language`, `-lang` | Filtrar por lenguaje de programación |
| `--min-stars`, `-s` | Número mínimo de estrellas |

## Uso (GUI)

```bash
python gui.py
```

Se abre una ventana con campos para:

- **Palabra clave** (obligatorio)
- **Lenguaje** (opcional)
- **Estrellas mínimas** (opcional)
- **Límite** (por defecto: 10)

Los resultados se muestran en una tabla con scroll.

## Límite de tasa

La API pública de GitHub tiene un límite de 60 solicitudes por hora sin autenticación. Para aumentarlo, define la variable de entorno `GITHUB_TOKEN` con un token de acceso personal.
