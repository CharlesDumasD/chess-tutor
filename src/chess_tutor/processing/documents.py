"""Clean raw chess corpus files into processed text files."""

import re
from pathlib import Path

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


def clean_gutenberg_text(text: str) -> str:
    """Remove standard Project Gutenberg boilerplate."""

    start_match = re.search(
        r"\*\*\* START OF (?:THE )?PROJECT GUTENBERG EBOOK.*\*\*\*",
        text,
    )
    end_match = re.search(
        r"\*\*\* END OF (?:THE )?PROJECT GUTENBERG EBOOK.*\*\*\*",
        text,
    )

    if start_match:
        text = text[start_match.end() :]

    if end_match:
        text = text[: end_match.start()]

    return text


def clean_text(text: str, provider: str) -> str:
    """Clean one raw document while keeping transformations conservative."""

    text = text.replace("\ufeff", "")

    if provider == "gutenberg":
        text = clean_gutenberg_text(text)

    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def process_raw_texts() -> None:
    """Clean raw text files and write them to data/processed/."""

    raw_files = sorted(RAW_DATA_DIR.glob("*/*.txt"))

    for raw_file in raw_files:
        provider = raw_file.parent.name
        processed_file = PROCESSED_DATA_DIR / provider / raw_file.name
        processed_file.parent.mkdir(parents=True, exist_ok=True)

        raw_text = raw_file.read_text(encoding="utf-8", errors="ignore")
        processed_text = clean_text(raw_text, provider)
        processed_file.write_text(processed_text, encoding="utf-8")

        print(f"processed: {processed_file}")


def main() -> None:
    """Run the text processing pipeline."""

    process_raw_texts()
