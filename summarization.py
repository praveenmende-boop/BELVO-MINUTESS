
import re
from collections import Counter


def summarize_meeting(text):

    if not text or not text.strip():
        return "No transcript available."

    try:
        # Divide transcript into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        sentences = [
            sentence.strip()
            for sentence in sentences
            if len(sentence.strip().split()) > 3
        ]

        if not sentences:
            return text[:500]

        # Calculate word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        stop_words = {
            "the", "and", "for", "are", "was",
            "were", "this", "that", "with",
            "from", "have", "has", "had",
            "you", "your", "they", "their",
            "will", "would", "could", "should",
            "about", "into", "there", "then"
        }

        frequencies = Counter(
            word for word in words
            if word not in stop_words
        )

        # Score each sentence
        scored_sentences = []

        for index, sentence in enumerate(sentences):

            sentence_words = re.findall(
                r'\b[a-zA-Z]{3,}\b',
                sentence.lower()
            )

            score = sum(
                frequencies[word]
                for word in sentence_words
            )

            scored_sentences.append(
                (score, index, sentence)
            )

        # Select important sentences
        count = min(5, len(scored_sentences))

        important = sorted(
            scored_sentences,
            key=lambda item: item[0],
            reverse=True
        )[:count]

        # Maintain original sentence order
        important.sort(key=lambda item: item[1])

        summary = " ".join(
            item[2] for item in important
        )

        return summary

    except Exception as e:
        return f"Summary generation failed: {e}"
