import re
from collections import Counter


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "it", "its", "this", "that",
    "these", "those", "we", "you", "they", "he", "she", "them", "their",
    "not", "no", "nor", "so", "if", "than", "then", "just", "also", "very",
    "too", "about", "into", "over", "such", "each", "which", "what", "who",
    "when", "where", "why", "how", "all", "both", "each", "few", "more",
    "most", "some", "any", "every", "both", "own", "same", "other", "another",
    "much", "many", "still", "even", "though", "although", "because", "since",
    "after", "before", "between", "under", "above", "below", "up", "down",
    "out", "off", "here", "there", "being", "been", "having", "doing",
    "get", "got", "getting", "make", "made", "making", "use", "used", "using",
    "like", "well", "back", "way", "new", "now", "one", "two",
    "first", "last", "long", "great", "little", "right", "old", "high",
    "different", "large", "small", "next", "early", "young", "important",
    "few", "same", "able", "often", "always", "never", "ever", "here",
    "there", "around", "together", "along", "almost", "enough", "already",
    "however", "instead", "therefore", "meanwhile", "nevertheless",
    "moreover", "furthermore", "besides", "otherwise", "indeed", "perhaps",
    "quite", "rather", "via", "per", "etc", "eg", "ie",
}


def _extract_keywords(text, top_n=25):
    text_lower = text.lower()
    words = re.findall(r"\b[a-zA-Z]\w+\b", text_lower)
    words = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    freq = Counter(words)
    return [kw for kw, _ in freq.most_common(top_n)]


def _split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 10]


def generate_mindmap(text, title="Study Notes"):
    sentences = _split_sentences(text)
    keywords = _extract_keywords(text)
    keyword_set = set(keywords)

    topic_sentences = {}
    for s in sentences:
        s_lower = s.lower()
        matched = [kw for kw in keywords if kw in s_lower]
        if matched:
            best = matched[0]
            if best not in topic_sentences:
                topic_sentences[best] = []
            if len(topic_sentences[best]) < 2:
                topic_sentences[best].append(s[:100].strip())

    used_sentences = set()
    for kw, sents in topic_sentences.items():
        for s in sents:
            used_sentences.add(s)

    lines = [f"# {title}"]
    for kw in keywords:
        if kw not in topic_sentences:
            continue
        lines.append(f"## {kw.title()}")
        for s in topic_sentences[kw][:2]:
            lines.append(f"- {s}")
    return "\n".join(lines)
