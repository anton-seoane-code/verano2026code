import os

try:
    import fitz
except ImportError:
    fitz = None


def scan_directory(directory):
    files = []
    if not os.path.isdir(directory):
        return files
    for entry in sorted(os.listdir(directory)):
        if entry.endswith((".txt", ".pdf")):
            full = os.path.join(directory, entry)
            if os.path.isfile(full):
                files.append({"name": entry, "path": full, "size": os.path.getsize(full)})
    return files


def read_text_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_pdf_file(path):
    if fitz is None:
        raise ImportError("PyMuPDF is required to read PDF files. Install with: pip install PyMuPDF")
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def read_file(path):
    if path.endswith(".pdf"):
        return read_pdf_file(path)
    else:
        return read_text_file(path)
