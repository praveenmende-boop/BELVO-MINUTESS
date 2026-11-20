
import re
from collections import Counter


def summarize_meeting(text):

    if not text or not text.strip():
        return "No transcript available."

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    if len(sentences) <= 3:
        return text

    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    stop_words = {
        "the", "is", "are", "was", "were", "a", "an",
        "and", "or", "to", "of", "in", "on", "for",
        "with", "that", "this", "it", "we", "they",
        "he", "she", "you", "i", "at", "as", "be"
    }

    word_freq = Counter(
        word for word in words if word not in stop_words
    )

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(
            r'\b[a-zA-Z]+\b', sentence.lower()
        )

        score = sum(
            word_freq[word] for word in sentence_words
        )

        scored_sentences.append((score, index, sentence))

    best_sentences = sorted(
        scored_sentences,
        key=lambda x: x[0],
        reverse=True
    )[:3]

    best_sentences.sort(key=lambda x: x[1])

    return " ".join(item[2] for item in best_sentences)
