
import re

def extract_decisions(text):
    decision_patterns = [
        r"(?:we have decided to|we decided to|decision is to|agreed to|it was decided that)\s+[^.!?\n]+",
        r"(?:the team will|management will|we will)\s+[^.!?\n]+"
    ]

    decisions = []

    for pattern in decision_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        decisions.extend(matches)

    # Remove duplicate decisions
    unique_decisions = list(dict.fromkeys(decisions))

    return unique_decisions
