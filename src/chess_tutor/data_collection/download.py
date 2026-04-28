"""Download entry point for public chess corpus sources."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from urllib.request import Request, urlopen

from chess_tutor.data_collection.sources import GUTENBERG_SOURCES, Source

GUTENBERG_RAW_DIR = Path("data/raw/gutenberg")
GUTENBERG_METADATA_FILE = GUTENBERG_RAW_DIR / "metadata.json"
USER_AGENT = "chess-tutor/0.1 educational RAG project"


def download_text(source: Source, destination: Path) -> str:
    """Download one Project Gutenberg UTF-8 text file."""

    if destination.exists():
        return "skipped"

    request = Request(source.download_url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")

    destination.write_text(text, encoding="utf-8")
    return "downloaded"


def build_metadata_record(
    source: Source,
    destination: Path,
    status: str,
) -> dict[str, str]:
    """Build metadata for a downloaded source file."""

    record = asdict(source)
    record.update(
        {
            "local_path": str(destination),
            "status": status,
            "collected_at": datetime.now(UTC).isoformat(),
        }
    )
    return record


def write_metadata(records: list[dict[str, str]]) -> None:
    """Write download metadata beside the raw files."""

    GUTENBERG_METADATA_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def download_gutenberg_books() -> None:
    """Download the six Project Gutenberg books used in the corpus."""

    GUTENBERG_RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []

    for source in GUTENBERG_SOURCES:
        destination = GUTENBERG_RAW_DIR / source.filename
        status = download_text(source, destination)
        record = build_metadata_record(source, destination, status)
        records.append(record)
        print(f"{status}: {destination}")
        sleep(1)

    write_metadata(records)
    print(f"Wrote metadata: {GUTENBERG_METADATA_FILE}")


def main() -> None:
    """Run the current data collection pipeline."""

    download_gutenberg_books()
