#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from repo_searcher import search_repositories


class RepoSearcherGUI:
    def __init__(self, root):
        self.root = root
        root.title("repo-searcher")
        root.geometry("900x600")
        root.minsize(700, 400)

        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input frame ---
        input_frame = ttk.LabelFrame(main_frame, text="Búsqueda", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Palabra clave:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.keyword_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.keyword_var, width=40).grid(row=0, column=1, sticky=tk.EW, padx=(0, 15))

        ttk.Label(input_frame, text="Lenguaje:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.language_var, width=15).grid(row=0, column=3, sticky=tk.EW, padx=(0, 15))

        ttk.Label(input_frame, text="Estrellas mín:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.min_stars_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.min_stars_var, width=10).grid(row=0, column=5, sticky=tk.EW, padx=(0, 15))

        ttk.Label(input_frame, text="Límite:").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        self.limit_var = tk.StringVar(value="10")
        ttk.Entry(input_frame, textvariable=self.limit_var, width=5).grid(row=0, column=7, sticky=tk.EW, padx=(0, 10))

        self.search_btn = ttk.Button(input_frame, text="Buscar", command=self.search)
        self.search_btn.grid(row=0, column=8)

        input_frame.columnconfigure(1, weight=1)

        # --- Results frame ---
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=6)
        results_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("#", "Repositorio", "Estrellas", "Lenguaje", "Descripción")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)

        self.tree.heading("#", text="#")
        self.tree.heading("Repositorio", text="Repositorio")
        self.tree.heading("Estrellas", text="Estrellas")
        self.tree.heading("Lenguaje", text="Lenguaje")
        self.tree.heading("Descripción", text="Descripción")

        self.tree.column("#", width=40, minwidth=30, anchor=tk.CENTER)
        self.tree.column("Repositorio", width=280, minwidth=150)
        self.tree.column("Estrellas", width=90, minwidth=70, anchor=tk.E)
        self.tree.column("Lenguaje", width=100, minwidth=60)
        self.tree.column("Descripción", width=350, minwidth=150)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Status bar ---
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(6, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.bind("<Return>", lambda e: self.search())

    def search(self):
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showwarning("Campo vacío", "Introduce una palabra clave para buscar.")
            return

        language = self.language_var.get().strip() or None
        min_stars_str = self.min_stars_var.get().strip()
        min_stars = None
        if min_stars_str:
            try:
                min_stars = int(min_stars_str)
                if min_stars < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Valor inválido", "Estrellas mínimas debe ser un número entero no negativo.")
                return

        limit_str = self.limit_var.get().strip()
        try:
            limit = int(limit_str)
            if limit < 1 or limit > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor inválido", "El límite debe ser un número entre 1 y 100.")
            return

        self.search_btn.config(state=tk.DISABLED)
        self.status_var.set("Buscando...")
        self.tree.delete(*self.tree.get_children())

        thread = threading.Thread(
            target=self._do_search,
            args=(keyword, limit, language, min_stars),
            daemon=True
        )
        thread.start()

    def _do_search(self, keyword, limit, language, min_stars):
        try:
            data = search_repositories(keyword, limit, language, min_stars)
            self.root.after(0, self._show_results, data, keyword)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_results(self, data, keyword):
        items = data.get("items", [])
        total = data.get("total_count", 0)

        if not items:
            self.status_var.set(f"Sin resultados para '{keyword}'.")
            self.search_btn.config(state=tk.NORMAL)
            return

        for i, repo in enumerate(items, 1):
            name = repo["full_name"]
            stars = repo["stargazers_count"]
            lang = repo["language"] or "—"
            desc = repo["description"] or "Sin descripción"
            self.tree.insert("", tk.END, values=(i, name, stars, lang, desc))

        self.status_var.set(f"{total} encontrados — mostrando {len(items)}")
        self.search_btn.config(state=tk.NORMAL)

    def _show_error(self, error_msg):
        messagebox.showerror("Error", error_msg)
        self.status_var.set("Error en la búsqueda")
        self.search_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    RepoSearcherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
