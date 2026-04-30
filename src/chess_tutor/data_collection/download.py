"""Download entry point for public chess corpus sources."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from chess_tutor.data_collection.sources import (
    GUTENBERG_SOURCES,
    INTERNET_ARCHIVE_SOURCES,
    WIKIPEDIA_SOURCES,
    Source,
)

GUTENBERG_RAW_DIR = Path("data/raw/gutenberg")
GUTENBERG_METADATA_FILE = GUTENBERG_RAW_DIR / "metadata.json"
INTERNET_ARCHIVE_RAW_DIR = Path("data/raw/internet_archive")
INTERNET_ARCHIVE_METADATA_FILE = INTERNET_ARCHIVE_RAW_DIR / "metadata.json"
WIKIPEDIA_RAW_DIR = Path("data/raw/wikipedia")
WIKIPEDIA_METADATA_FILE = WIKIPEDIA_RAW_DIR / "metadata.json"
USER_AGENT = "chess-tutor/0.1 educational RAG project"
MAX_DOWNLOAD_ATTEMPTS = 5


def sleep_before_retry(error: Exception, attempt: int) -> None:
    """Sleep before retrying a transient download error."""

    retry_after = None

    if isinstance(error, HTTPError):
        retry_after = error.headers.get("Retry-After")

    if retry_after and retry_after.isdigit():
        sleep_seconds = int(retry_after)
    else:
        sleep_seconds = min(60, 2**attempt)

    print(f"retrying in {sleep_seconds}s after: {error}")
    sleep(sleep_seconds)


def open_url_with_retries(request: Request):
    """Open a URL with retries for rate limits and transient timeouts."""

    last_error = None

    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        try:
            return urlopen(request, timeout=60)
        except HTTPError as error:
            last_error = error
            if error.code != 429 or attempt == MAX_DOWNLOAD_ATTEMPTS:
                raise
            sleep_before_retry(error, attempt)
        except (TimeoutError, URLError) as error:
            last_error = error
            if attempt == MAX_DOWNLOAD_ATTEMPTS:
                raise
            sleep_before_retry(error, attempt)

    raise RuntimeError(f"Download failed: {last_error}")


def download_text(source: Source, destination: Path) -> str:
    """Download one UTF-8 text file."""

    if destination.exists() and not looks_like_html(destination):
        return "skipped"

    request = Request(source.download_url, headers={"User-Agent": USER_AGENT})

    with open_url_with_retries(request) as response:
        text = response.read().decode("utf-8")

    destination.write_text(text, encoding="utf-8")
    return "downloaded"


def looks_like_html(path: Path) -> bool:
    """Return True if a saved text file is actually an HTML page."""

    start = path.read_text(encoding="utf-8", errors="ignore")[:500].lower()
    return "<!doctype html" in start or "<html" in start


def download_wikipedia_text(source: Source, destination: Path) -> str:
    """Download one Wikipedia article as plain text."""

    if destination.exists():
        return "skipped"

    request = Request(source.download_url, headers={"User-Agent": USER_AGENT})

    with open_url_with_retries(request) as response:
        data = json.loads(response.read().decode("utf-8"))

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    if "missing" in page:
        raise RuntimeError(f"Wikipedia article not found: {source.title}")

    destination.write_text(page.get("extract", ""), encoding="utf-8")
    return "downloaded"


def build_metadata_record(
    source: Source,
    destination: Path,
    status: str,
    error: str = "",
) -> dict[str, str]:
    """Build metadata for a downloaded source file."""

    record = asdict(source)
    record.update(
        {
            "local_path": str(destination),
            "status": status,
            "collected_at": datetime.now(UTC).isoformat(),
            "error": error,
        }
    )
    return record


def write_metadata(records: list[dict[str, str]], metadata_file: Path) -> None:
    """Write download metadata beside the raw files."""

    metadata_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def print_record_status(record: dict[str, str], destination: Path) -> None:
    """Print one download status line."""

    message = f"{record['status']}: {destination}"

    if record["error"]:
        message = f"{message} ({record['error']})"

    print(message)


def download_gutenberg_books() -> None:
    """Download the six Project Gutenberg books used in the corpus."""

    GUTENBERG_RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []

    for source in GUTENBERG_SOURCES:
        destination = GUTENBERG_RAW_DIR / source.filename
        try:
            status = download_text(source, destination)
            record = build_metadata_record(source, destination, status)
        except (HTTPError, URLError, RuntimeError) as error:
            record = build_metadata_record(source, destination, "failed", str(error))
        records.append(record)
        print_record_status(record, destination)
        sleep(1)

    write_metadata(records, GUTENBERG_METADATA_FILE)
    print(f"Wrote metadata: {GUTENBERG_METADATA_FILE}")


def download_internet_archive_books() -> None:
    """Download the Internet Archive full-text books used in the corpus."""

    INTERNET_ARCHIVE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []

    for source in INTERNET_ARCHIVE_SOURCES:
        destination = INTERNET_ARCHIVE_RAW_DIR / source.filename
        try:
            status = download_text(source, destination)
            record = build_metadata_record(source, destination, status)
        except (HTTPError, URLError, RuntimeError) as error:
            record = build_metadata_record(source, destination, "failed", str(error))
        records.append(record)
        print_record_status(record, destination)
        sleep(1)

    write_metadata(records, INTERNET_ARCHIVE_METADATA_FILE)
    print(f"Wrote metadata: {INTERNET_ARCHIVE_METADATA_FILE}")


def download_wikipedia_articles() -> None:
    """Download the curated Wikipedia articles used in the corpus."""

    WIKIPEDIA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []

    for source in WIKIPEDIA_SOURCES:
        destination = WIKIPEDIA_RAW_DIR / source.filename
        try:
            status = download_wikipedia_text(source, destination)
            record = build_metadata_record(source, destination, status)
        except (HTTPError, URLError, RuntimeError, KeyError, StopIteration) as error:
            record = build_metadata_record(source, destination, "failed", str(error))
        records.append(record)
        print_record_status(record, destination)
        sleep(1)

    write_metadata(records, WIKIPEDIA_METADATA_FILE)
    print(f"Wrote metadata: {WIKIPEDIA_METADATA_FILE}")


def main() -> None:
    """Run the current data collection pipeline."""

    download_gutenberg_books()
    download_internet_archive_books()
    download_wikipedia_articles()
