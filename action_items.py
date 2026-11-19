
import re

def extract_action_items(text):
    patterns = [
        r"(?:action item|task|responsibility)\s*[:\-]?\s*[^.!?\n]+",
        r"(?:will complete|will prepare|will submit|needs to|has to|must)\s+[^.!?\n]+",
        r"(?:assigned to|responsible for)\s+[^.!?\n]+"
    ]

    action_items = []

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        action_items.extend(matches)

    # Remove duplicate tasks
    unique_items = list(dict.fromkeys(action_items))

    return unique_items
