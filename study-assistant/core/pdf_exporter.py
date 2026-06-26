import re
from io import BytesIO

from fpdf import FPDF


class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _strip_md(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s


def export_markdown_to_pdf(markdown_text, title="Summary"):
    pdf = MarkdownPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(10, 132, 255)
    pdf.cell(0, 14, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    lines = markdown_text.split("\n")
    for line in lines:
        stripped = line.strip()

        if stripped == "":
            pdf.ln(3)
            continue

        if stripped.startswith("# "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 8, _strip_md(stripped[2:]))

        elif stripped.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 7, _strip_md(stripped[3:]))

        elif stripped.startswith("### "):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 6, _strip_md(stripped[4:]))

        elif stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            x = pdf.get_x()
            pdf.cell(6, 5, "  -")
            pdf.set_x(x + 6)
            pdf.multi_cell(0, 5, _strip_md(stripped[2:]))
            pdf.set_x(x)

        elif stripped.startswith(("**", "*", "1.", "2.", "3.")):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5.5, _strip_md(stripped))

        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5.5, _strip_md(stripped))

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
