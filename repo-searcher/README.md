# repo-searcher

CLI para buscar repositorios en GitHub por palabra clave, mostrando nombre, estrellas, lenguaje y descripción.

## Requisitos

- Python 3.8+

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python repo_searcher.py "machine learning"
python repo_searcher.py "web framework" --limit 20
python repo_searcher.py rust
```

## Salida

```
┌───────┬──────────────────────────────┬───────────┬──────────┬──────────────────────────────┐
│   #   │ Repositorio                  │ Estrellas │ Lenguaje │ Descripción                  │
├───────┼──────────────────────────────┼───────────┼──────────┼──────────────────────────────┤
│   1   │ tensorflow/tensorflow        │    188654 │ Python   │ An Open Source Machine…      │
│   2   │ facebook/react               │    185432 │ JavaScript│ A declarative…               │
│   3   │ twbs/bootstrap               │    171234 │ JavaScript│ The most popular…            │
└───────┴──────────────────────────────┴───────────┴──────────┴──────────────────────────────┘
```

## Límite de tasa

La API pública de GitHub tiene un límite de 60 solicitudes por hora sin autenticación. Para aumentarlo, define la variable de entorno `GITHUB_TOKEN` con un token de acceso personal.
