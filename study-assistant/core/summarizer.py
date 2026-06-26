import re
import math
from collections import Counter


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _tokenize(text):
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def _score_sentences(sentences):
    if not sentences:
        return []

    word_freq = Counter()
    for s in sentences:
        word_freq.update(_tokenize(s))

    max_freq = max(word_freq.values()) if word_freq else 1

    total_sentences = len(sentences)
    scored = []
    for i, s in enumerate(sentences):
        tokens = _tokenize(s)
        if not tokens:
            scored.append((s, 0))
            continue

        freq_score = sum(word_freq[t] / max_freq for t in tokens) / len(tokens)
        position_score = 1.0 - (i / total_sentences)
        length_bonus = min(len(tokens) / 20, 1.0)

        total = freq_score * 0.4 + position_score * 0.3 + length_bonus * 0.3
        scored.append((s, total))

    return scored


def generate_summary(text, ratio=0.2, min_sentences=3, max_sentences=20):
    sentences = _split_sentences(text)
    if len(sentences) <= min_sentences:
        return "\n\n".join(sentences)

    scored = _score_sentences(sentences)
    n = max(min_sentences, min(max_sentences, math.ceil(len(sentences) * ratio)))
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:n]
    selected_indices = sorted(sentences.index(s) for s, _ in ranked)
    selected = [sentences[i] for i in selected_indices]

    return "\n\n".join(selected)
