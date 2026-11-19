
from transformers import pipeline

summarizer = None

def summarize_meeting(text):
    global summarizer

    if not text.strip():
        return "No transcript available."

    try:
        if summarizer is None:
            summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=-1
            )

        short_text = text[:800]

        result = summarizer(
            short_text,
            max_length=80,
            min_length=15,
            do_sample=False,
            truncation=True
        )

        return result[0]["summary_text"]

    except Exception as e:
        return f"Summary generation failed: {e}"
