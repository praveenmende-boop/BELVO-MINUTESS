
import re


def track_name_mentions(segments, name, variations=None):
    if not name or not name.strip():
        return []

    names = [name.strip()]

    if variations:
        names.extend(
            item.strip()
            for item in variations
            if item.strip()
        )

    names = sorted(set(names), key=len, reverse=True)

    pattern = re.compile(
        r"(?<!\w)(?:" +
        "|".join(re.escape(item) for item in names) +
        r")(?!\w)",
        re.IGNORECASE
    )

    mentions = []

    for segment in segments:
        text = segment["text"]

        if pattern.search(text):
            mentions.append({
                "name": name,
                "timestamp": segment["start"],
                "end": segment["end"],
                "context": text
            })

    return mentions
