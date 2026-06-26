import re
import random
from collections import Counter


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "it", "its", "this", "that", "these", "those", "we", "you", "they",
    "he", "she", "them", "their", "not", "no", "so", "if", "than", "then",
    "just", "also", "very", "too", "about", "into", "over", "such", "each",
    "which", "what", "who", "when", "where", "why", "how", "all", "both",
    "more", "most", "some", "any", "every", "own", "other", "much", "many",
    "still", "even", "though", "because", "since", "after", "before",
    "being", "been", "having", "doing", "get", "got", "make", "made",
    "use", "used", "like", "well", "back", "way", "new", "now", "one", "two",
    "first", "last", "long", "great", "little", "right", "old", "high",
    "different", "large", "small", "next", "early", "young", "important",
    "same", "able", "often", "always", "never", "ever", "here", "there",
    "around", "together", "along", "almost", "enough", "already",
    "however", "instead", "therefore", "meanwhile", "nevertheless",
    "moreover", "furthermore", "besides", "otherwise", "indeed", "perhaps",
    "quite", "rather", "via", "per", "etc", "eg", "ie", "has", "have",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "can",
}


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) > 20]


def _get_key_terms(text):
    words = re.findall(r"\b[a-zA-Z]\w+\b", text.lower())
    words = [w for w in words if w not in _STOPWORDS and len(w) > 3]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(30)]


def _find_blank_target(sentence, key_terms):
    sent_lower = sentence.lower()
    for term in key_terms:
        pattern = r"\b" + re.escape(term) + r"\b"
        match = re.search(pattern, sent_lower)
        if match:
            return sentence[match.start():match.end()]
    return None


def _generate_distractors(correct, key_terms, n=2):
    candidates = [t for t in key_terms if t.lower() != correct.lower()]
    random.shuffle(candidates)
    return candidates[:n]


def generate_quiz(text, num_questions=5):
    sentences = _split_sentences(text)
    random.shuffle(sentences)
    key_terms = _get_key_terms(text)

    questions = []
    for sent in sentences:
        if len(questions) >= num_questions:
            break
        target = _find_blank_target(sent, key_terms)
        if not target:
            continue
        distractors = _generate_distractors(target, key_terms)
        if len(distractors) < 2:
            continue

        blanked = sent.replace(target, "______", 1)
        options = [target] + distractors[:2]
        random.shuffle(options)
        labels = ["a", "b", "c"]
        labeled = {labels[i]: options[i] for i in range(3)}
        correct_label = next(l for l, v in labeled.items() if v == target)

        questions.append({
            "question": blanked,
            "options": labeled,
            "answer": correct_label,
            "correct_text": target,
        })

    return questions


def format_quiz_markdown(questions, title="Quiz"):
    lines = [f"# {title}", ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"**{i}. {q['question']}**")
        for label in ["a", "b", "c"]:
            lines.append(f"   {label}) {q['options'][label]}")
        lines.append(f"   *Answer: {q['answer']}*")
        lines.append("")
    return "\n".join(lines)
