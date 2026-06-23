#!/usr/bin/env python3
import argparse
import sys

import requests
from rich.console import Console
from rich.table import Table


def search_repositories(keyword, limit=10, language=None, min_stars=None):
    url = "https://api.github.com/search/repositories"
    query = keyword
    if language:
        query += f" language:{language}"
    if min_stars is not None:
        query += f" stars:>={min_stars}"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": limit}
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "repo-searcher/1.0",
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        if resp.status_code == 403:
            print("Error 403: límite de tasa de GitHub alcanzado. Espera un momento o usa autenticación.")
        elif resp.status_code == 422:
            print("Error 422: consulta inválida.")
        else:
            print(f"Error HTTP {resp.status_code}: la solicitud falló.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error de conexión: no se pudo conectar con GitHub.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: la solicitud a GitHub tardó demasiado.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


def show_results(data, keyword):
    console = Console()
    items = data.get("items", [])
    total = data.get("total_count", 0)

    if not items:
        console.print(f"[yellow]No se encontraron repositorios para '{keyword}'.[/yellow]")
        return

    console.print(
        f"\n[bold cyan]Resultados para:[/bold cyan] [white]{keyword}[/white]  "
        f"[dim]({total} encontrados, mostrando {len(items)})[/dim]\n"
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Repositorio", style="cyan", no_wrap=True)
    table.add_column("Estrellas", justify="right", style="green")
    table.add_column("Lenguaje", style="blue")
    table.add_column("Descripción")

    for i, repo in enumerate(items, 1):
        name = repo["full_name"]
        stars = str(repo["stargazers_count"])
        lang = repo["language"] or "—"
        desc = repo["description"]
        if desc and len(desc) > 80:
            desc = desc[:77] + "…"
        elif not desc:
            desc = "Sin descripción"
        table.add_row(str(i), name, stars, lang, desc)

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Busca repositorios en GitHub por palabra clave."
    )
    parser.add_argument("keyword", help="Palabra clave para buscar repositorios")
    parser.add_argument(
        "-l", "--limit", type=int, default=10,
        help="Número máximo de resultados (por defecto: 10, máximo: 100)"
    )
    parser.add_argument(
        "--language", "-lang", type=str, default=None,
        help="Filtrar por lenguaje de programación (ej. python, rust, javascript)"
    )
    parser.add_argument(
        "--min-stars", "-s", type=int, default=None,
        help="Número mínimo de estrellas (ej. 1000)"
    )
    args = parser.parse_args()

    if args.limit < 1:
        print("El límite debe ser al menos 1.")
        sys.exit(1)
    if args.limit > 100:
        print("El límite máximo es 100 (impuesto por la API de GitHub).")
        sys.exit(1)
    if args.min_stars is not None and args.min_stars < 0:
        print("El número mínimo de estrellas no puede ser negativo.")
        sys.exit(1)

    data = search_repositories(args.keyword, args.limit, args.language, args.min_stars)
    show_results(data, args.keyword)


if __name__ == "__main__":
    main()
