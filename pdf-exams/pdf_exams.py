#!/usr/bin/env python3
import sys
import re
import random


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
    'has', 'have', 'had', 'does', 'does', 'did', 'will', 'would', 'can',
    'could', 'should', 'may', 'might', 'shall', 'about', 'above', 'across',
    'after', 'along', 'among', 'around', 'before', 'behind', 'below',
    'beneath', 'beside', 'between', 'beyond', 'down', 'inside', 'outside',
    'under', 'until', 'up', 'upon', 'within', 'without', 'into', 'onto',
    'onto', 'from', 'with', 'through', 'during', 'such', 'other', 'another',
    'both', 'each', 'few', 'more', 'most', 'several', 'new', 'old',
    'like', 'including', 'according', 'well', 'back', 'even', 'still',
    'already', 'yet', 'about', 'again', 'ever', 'never', 'always',
}


def extract_text(pdf_path):
    try:
        import fitz
    except ImportError:
        print("Error: PyMuPDF is required. Install with: pip install PyMuPDF", file=sys.stderr)
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


def split_sentences(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def extract_key_terms(sentence):
    terms = []
    clean = re.sub(r'[^\w\s]', ' ', sentence)
    tokens = clean.split()
    token_set = set(t.lower() for t in tokens)

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


def generate_questions(text, max_questions=10):
    sentences = split_sentences(text)

    sentence_data = []
    all_terms = []

    for sent in sentences:
        terms = extract_key_terms(sent)
        if not terms:
            continue
        priority = {'acronym': 0, 'proper': 1, 'number': 2}
        best_term, best_cat = min(terms, key=lambda t: priority.get(t[1], 99))
        sentence_data.append((sent, best_term, best_cat))
        all_terms.append((best_term, best_cat))

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
        pattern = re.compile(re.escape(answer), re.IGNORECASE)
        question_text = pattern.sub('______', sent, count=1)

        # Deduplicate distractor pool
        seen_terms = set()
        unique_terms = []
        for t, c in all_terms:
            low = t.lower()
            if low not in seen_terms and low != answer.lower():
                seen_terms.add(low)
                unique_terms.append((t, c))

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
            'correct_index': options.index(answer)
        })

    return questions


def run_exam(questions):
    answers = []
    total = len(questions)
    labels = ['a', 'b', 'c']

    print(f"\n{'=' * 60}")
    print(f"  PDF EXAM — {total} Questions")
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

    print(f"\n{'=' * 60}")
    print(f"  RESULTS — {correct_count}/{total} correct ({correct_count / total * 100:.0f}%)")
    print(f"{'=' * 60}\n")

    for i, a in enumerate(answers, 1):
        status = "✓" if a['correct'] else "✗"
        chosen_text = a['options'][ord(a['chosen']) - ord('a')]
        print(f"{status} Q{i}: {a['question']}")
        print(f"   Your answer: [{a['chosen']}] {chosen_text}")
        print(f"   Correct: [{a['correct_label']}] {a['answer']}\n")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <pdf-file>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"Reading PDF: {pdf_path}")

    text = extract_text(pdf_path)

    if not text.strip():
        print("Error: No text extracted from PDF.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(text)} characters of text.")

    questions = generate_questions(text)
    print(f"Generated {len(questions)} questions.")

    if questions:
        run_exam(questions)
    else:
        print("Could not generate questions. The PDF may not contain enough text content.")
        sys.exit(1)


if __name__ == '__main__':
    main()
