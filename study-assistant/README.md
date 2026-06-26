# Study Assistant

CLI + Web GUI tool that scans directories with `.txt` and `.pdf` files, then generates:

- **Summaries** — extractive markdown summaries
- **Mind maps** — Markmap-format interactive mind maps
- **Quizzes** — multiple-choice questions (a/b/c)

## Quick Start

```bash
pip install PyMuPDF

# Web GUI
python server.py
# → http://localhost:8000

# CLI
python main.py --dir samples --all
```

## Usage

### Web GUI

1. Run `python server.py` and open `http://localhost:8000`
2. Enter a directory path and click **Scan**
3. Select files and output types (Summaries / Mind Maps / Quizzes)
4. Click **Generate** — results appear inline

### CLI

```bash
python main.py --dir /path/to/study/files --all
python main.py --dir /path/to/study/files --summaries --mindmaps
python main.py --dir samples --quizzes
```

Output is written to `output/{summaries,mindmaps,quizzes}/`.

## Project Structure

```
study-assistant/
├── main.py              # CLI entry point
├── server.py            # HTTP server (REST API + static files)
├── core/
│   ├── reader.py        # Directory scanning, .txt/.pdf reading
│   ├── summarizer.py    # Extractive summarization
│   ├── mindmap_gen.py   # Keyword → markmap hierarchical tree
│   └── quiz_gen.py      # MCQ generation (a/b/c)
├── static/              # Web frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── samples/             # Sample files for testing
└── output/              # Generated outputs
```

## Dependencies

- Python 3.10+
- PyMuPDF (`pip install PyMuPDF`)

## Changelog

### 26/06/2026

- Project scaffold: directory structure, README, requirements.txt, skeleton CLI + server
- File reader: directory scan, `.txt`/`.pdf` reading via PyMuPDF
- Summarizer: extractive summarization (frequency + position + length scoring)
- Mind map generator: keyword extraction and topic clustering → markmap format
- Quiz generator: term blanking + distractor selection → MCQ with a/b/c
- Web server: `/api/scan` and `/api/generate` endpoints
- Web GUI: dark glassmorphism UI with markmap.js and interactive quiz
- CLI: `main.py` with `--dir` and `--summaries`/`--mindmaps`/`--quizzes`/`--all` flags
- Sample files and end-to-end verification
