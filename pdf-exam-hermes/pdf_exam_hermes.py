#!/usr/bin/env python3
"""pdf-exam-hermes — Generate multiple-choice exams from any PDF."""

import sys
import re
import random
import argparse
from pathlib import Path


BANNED = {
    'created', 'developed', 'designed', 'founded', 'released', 'introduced',
    'published', 'invented', 'discovered', 'established', 'launched',
    'known', 'called', 'named', 'defined', 'written', 'used', 'based',
    'built', 'made', 'given', 'shown', 'found', 'held', 'taken',
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    'one', 'two', 'three', 'four', 'five', 'first', 'second', 'third',
    'many', 'much', 'some', 'any', 'every', 'all', 'both', 'each',
    'also', 'just', 'very', 'too', 'only', 'its', 'their', 'his', 'her',
    'which', 'what', 'where', 'when', 'who', 'why', 'how', 'not', 'no',
    'has', 'have', 'had', 'does', 'did', 'will', 'would', 'can',
    'could', 'should', 'may', 'might', 'shall', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'am',
    'about', 'above', 'across', 'after', 'along', 'among', 'around',
    'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond',
    'down', 'inside', 'outside', 'under', 'until', 'up', 'upon', 'within',
    'without', 'into', 'onto', 'from', 'with', 'through', 'during',
    'such', 'other', 'another', 'few', 'more', 'most', 'several',
    'like', 'including', 'according', 'well', 'back', 'even', 'still',
    'already', 'yet', 'again', 'ever', 'never', 'always',
    'while', 'because', 'since', 'although', 'though', 'unless',
    'than', 'then', 'else', 'otherwise', 'nor',
}


def extract_text(pdf_path: str) -> str:
    """Extract and clean text from a PDF using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        print("Error: PyMuPDF is required. Install with: pip install PyMuPDF",
              file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        lines = page_text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                cleaned.append('')
            elif cleaned and cleaned[-1] and cleaned[-1][-1] not in '.!?':
                cleaned[-1] += ' ' + line
            else:
                cleaned.append(line)
        text += ' '.join(cleaned) + '\n'
    doc.close()
    return text


def split_sentences(text: str, min_len: int = 20, max_len: float = float('inf')) -> list[str]:
    """Split text into sentences, filtering by length."""
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if min_len < len(s.strip()) < max_len]


def extract_key_terms(sentence: str) -> list[tuple[str, str]]:
    """Extract candidate answer terms: proper nouns, acronyms, numbers."""
    terms = []
    clean = re.sub(r'[^\w\s]', ' ', sentence)
    tokens = clean.split()

    for i, token in enumerate(tokens):
        if len(token) < 3 or token.lower() in BANNED:
            continue

        is_proper = token[0].isupper() and not token.isupper() and i > 0
        is_acronym = token.isupper() and 2 <= len(token) <= 8
        is_number = bool(re.match(r'^\d+[.,]?\d*%?$', token)) and len(token) <= 10

        if is_acronym:
            terms.append((token, 'acronym'))
        elif is_number:
            terms.append((token, 'number'))
        elif is_proper:
            if token.endswith('ed') and i > 0 and tokens[i - 1].lower() in ('is', 'are', 'was', 'were'):
                continue
            terms.append((token, 'proper'))

    return terms


def generate_questions(text: str, max_questions: int = 10, difficulty: str = 'mid') -> list[dict]:
    """Generate multiple-choice questions from extracted text."""
    diff_conf = {
        'easy': {'min_len': 20,  'max_len': 100, 'priority': {'proper': 0, 'acronym': 1, 'number': 2}},
        'mid':  {'min_len': 20,  'max_len': float('inf'), 'priority': {'acronym': 0, 'proper': 1, 'number': 2}},
        'hard': {'min_len': 40,  'max_len': 250, 'priority': {'number': 0, 'proper': 1, 'acronym': 2}},
    }
    cfg = diff_conf.get(difficulty, diff_conf['mid'])

    sentences = split_sentences(text, min_len=cfg['min_len'], max_len=cfg['max_len'])

    sentence_data = []
    all_terms = []

    for sent in sentences:
        terms = extract_key_terms(sent)
        if not terms:
            continue
        best_term, best_cat = min(terms, key=lambda t: cfg['priority'].get(t[1], 99))
        sentence_data.append((sent, best_term, best_cat))
        all_terms.append((best_term, best_cat))

    # Deduplicate by term+category
    seen = set()
    unique = []
    for sent, term, cat in sentence_data:
        key = f"{term}:{cat}"
        if key not in seen:
            seen.add(key)
            unique.append((sent, term, cat))

    random.shuffle(unique)
    selected = unique[:max_questions]

    if not selected:
        print("Error: Could not generate any questions from this PDF.", file=sys.stderr)
        sys.exit(1)

    questions = []

    for sent, answer, ans_cat in selected:
        # Build question by blanking the answer
        question_text = re.sub(re.escape(answer), '______', sent, count=1)

        # Collect distractors
        seen_terms = set()
        unique_terms = []
        for t, c in all_terms:
            low = t.lower()
            if low not in seen_terms and low != answer.lower():
                seen_terms.add(low)
                unique_terms.append((t, c))

        if difficulty == 'easy':
            # Easy: distractors from different category
            opposite = {'proper': ['acronym', 'number'],
                        'acronym': ['proper', 'number'],
                        'number': ['proper', 'acronym']}
            opp_cats = opposite.get(ans_cat, ['proper', 'acronym'])
            pool = [t for t, c in unique_terms if c in opp_cats]
            random.shuffle(pool)
            distractors = pool[:2]
            if len(distractors) < 2:
                rest = [t for t, c in unique_terms if c not in opp_cats]
                random.shuffle(rest)
                distractors += rest[:2 - len(distractors)]
        elif difficulty == 'hard':
            # Hard: distractors from same category
            same_cat = [t for t, c in unique_terms if c == ans_cat]
            random.shuffle(same_cat)
            distractors = same_cat[:2]
            if len(distractors) < 2:
                other = [t for t, c in unique_terms if c != ans_cat]
                random.shuffle(other)
                distractors += other[:2 - len(distractors)]
        else:
            # Mid: mix of same and different
            same_cat = [t for t, c in unique_terms if c == ans_cat]
            other = [t for t, c in unique_terms if c != ans_cat]
            random.shuffle(same_cat)
            random.shuffle(other)
            distractors = same_cat[:2] if len(same_cat) >= 2 else same_cat + other[:2 - len(same_cat)]

        if len(distractors) < 2:
            continue

        options = [answer] + distractors[:2]
        random.shuffle(options)

        questions.append({
            'question': question_text,
            'options': options,
            'answer': answer,
            'correct_index': options.index(answer),
        })

    return questions


def run_exam(questions: list[dict], difficulty: str = 'mid') -> None:
    """Present the exam interactively and show results."""
    answers = []
    total = len(questions)
    labels = ['a', 'b', 'c']

    diff_label = difficulty.upper()
    print(f"\n{'=' * 60}")
    print(f"  PDF EXAM — {diff_label} — {total} Question{'s' if total > 1 else ''}")
    print(f"{'=' * 60}\n")

    for i, q in enumerate(questions, 1):
        print(f"Question {i}/{total}:")
        print(f"  {q['question']}\n")
        for label, option in zip(labels, q['options']):
            print(f"  [{label}] {option}")

        while True:
            choice = input("\n  Your answer (a/b/c): ").strip().lower()
            if choice in labels:
                break
            print("  Invalid choice. Enter a, b, or c.")

        answers.append({
            'chosen': choice,
            'correct_label': labels[q['correct_index']],
            'correct': choice == labels[q['correct_index']],
            'question': q['question'],
            'options': q['options'],
            'answer': q['answer'],
        })
        print()

    correct_count = sum(1 for a in answers if a['correct'])
    pct = correct_count / total * 100

    print(f"\n{'=' * 60}")
    print(f"  RESULTS — {correct_count}/{total} correct ({pct:.0f}%)")
    print(f"{'=' * 60}\n")

    for i, a in enumerate(answers, 1):
        status = "✓" if a['correct'] else "✗"
        chosen_text = a['options'][ord(a['chosen']) - ord('a')]
        print(f"{status} Q{i}: {a['question']}")
        print(f"   Your answer: [{a['chosen']}] {chosen_text}")
        print(f"   Correct: [{a['correct_label']}] {a['answer']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate multiple-choice exam questions from a PDF file.'
    )
    parser.add_argument('pdf', type=str,
                        help='Path to the PDF file')
    parser.add_argument('-d', '--difficulty',
                        choices=['easy', 'mid', 'hard'],
                        default='mid',
                        help='Difficulty level (default: mid)')
    parser.add_argument('-q', '--questions',
                        type=int,
                        default=10,
                        help='Number of questions to generate (default: 10)')
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading PDF: {pdf_path}")
    print(f"Difficulty:  {args.difficulty}")
    print(f"Questions:   {args.questions}")

    text = extract_text(str(pdf_path))

    if not text.strip():
        print("Error: No text could be extracted from the PDF.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(text):,} characters of text.\n")

    questions = generate_questions(
        text,
        max_questions=args.questions,
        difficulty=args.difficulty,
    )
    print(f"Generated {len(questions)} question{'s' if len(questions) != 1 else ''}.\n")

    if questions:
        run_exam(questions, difficulty=args.difficulty)
    else:
        print("Could not generate questions. The PDF may not contain enough text content.")
        sys.exit(1)


if __name__ == '__main__':
    main()
