# Study Assistant

CLI + Web GUI tool that scans directories with `.txt` and `.pdf` files, then generates:

- **Summaries** — extractive markdown summaries
- **Mind maps** — Markmap-format interactive mind maps
- **Quizzes** — multiple-choice questions (a/b/c)

## Usage

### Web GUI

```bash
python server.py
# → http://localhost:8000
```

### CLI

```bash
python main.py --dir /path/to/study/files --all
python main.py --dir /path/to/study/files --summaries --mindmaps
```

## Dependencies

- Python 3.10+
- PyMuPDF (`pip install PyMuPDF`)

## Changelog

### 26/06/2026

- Project scaffold: directory structure, README, requirements.txt, skeleton CLI + server
