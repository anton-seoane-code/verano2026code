# PDF Exam Generator (Hermes)

Generate multiple-choice exams from any PDF file. Built with Hermes Agent.

## Features

- Extracts text from any PDF (via PyMuPDF)
- Generates A/B/C multiple-choice questions
- Three difficulty levels (easy / mid / hard)
- Configurable question count
- Interactive CLI exam with results at the end

## Requirements

- Python 3.8+
- PyMuPDF (`pip install PyMuPDF`)

## Usage

```bash
pip install -r requirements.txt
python pdf_exam_hermes.py path/to/document.pdf
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-d` | Difficulty: `easy`, `mid`, or `hard` | `mid` |
| `-q` | Number of questions to generate | `10` |

### Difficulty levels

| Level | Behaviour |
|-------|-----------|
| **easy** | Distractors from a different category than the answer — obvious wrong choices |
| **mid** | Mix of same-category and different-category distractors |
| **hard** | Distractors from the same category as the answer — subtle distinctions |
