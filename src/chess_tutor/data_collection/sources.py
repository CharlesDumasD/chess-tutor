"""Source metadata models for chess corpus collection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """A source document considered for the chess tutor corpus."""

    source_id: str
    provider: str
    author: str
    title: str
    license_name: str
    source_url: str
    download_url: str
    filename: str
    notes: str = ""


GUTENBERG_SOURCES = [
    Source(
        source_id="33870",
        provider="project_gutenberg",
        author="José Raúl Capablanca",
        title="Chess Fundamentals",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/33870",
        download_url="https://www.gutenberg.org/ebooks/33870.txt.utf-8",
        filename="33870_chess_fundamentals.txt",
    ),
    Source(
        source_id="5614",
        provider="project_gutenberg",
        author="Edward Lasker",
        title="Chess Strategy",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/5614",
        download_url="https://www.gutenberg.org/ebooks/5614.txt.utf-8",
        filename="5614_chess_strategy.txt",
        notes="Translated by J. Du Mont.",
    ),
    Source(
        source_id="4913",
        provider="project_gutenberg",
        author="Edward Lasker",
        title="Chess and Checkers: The Way to Mastership",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/4913",
        download_url="https://www.gutenberg.org/ebooks/4913.txt.utf-8",
        filename="4913_chess_and_checkers.txt",
        notes="Includes checkers material as well as chess.",
    ),
    Source(
        source_id="16377",
        provider="project_gutenberg",
        author="Howard Staunton",
        title=(
            "The Blue Book of Chess: Teaching the Rudiments of the Game, "
            "and Giving an Analysis of All the Recognized Openings"
        ),
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/16377",
        download_url="https://www.gutenberg.org/ebooks/16377.txt.utf-8",
        filename="16377_blue_book_of_chess.txt",
    ),
    Source(
        source_id="4902",
        provider="project_gutenberg",
        author="H. E. Bird",
        title="Chess History and Reminiscences",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/4902",
        download_url="https://www.gutenberg.org/ebooks/4902.txt.utf-8",
        filename="4902_chess_history_and_reminiscences.txt",
    ),
    Source(
        source_id="55278",
        provider="project_gutenberg",
        author="Franklin K. Young",
        title="Chess Generalship, Vol. I. Grand Reconnaissance",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/55278",
        download_url="https://www.gutenberg.org/ebooks/55278.txt.utf-8",
        filename="55278_chess_generalship_vol_1.txt",
    ),
]


INTERNET_ARCHIVE_SOURCES = [
    Source(
        source_id="commonsenseinche00laskrich",
        provider="internet_archive",
        author="Emanuel Lasker",
        title="Common Sense in Chess",
        license_name="NOT_IN_COPYRIGHT",
        source_url="https://archive.org/details/commonsenseinche00laskrich",
        download_url=(
            "https://archive.org/stream/commonsenseinche00laskrich/"
            "commonsenseinche00laskrich_djvu.txt"
        ),
        filename="commonsenseinche00laskrich_common_sense_in_chess.txt",
        notes="Internet Archive full text generated from OCR.",
    ),
    Source(
        source_id="dli.ministry.13269",
        provider="internet_archive",
        author="Siegbert Tarrasch",
        title=(
            "The Game of Chess: A Systematic Text Book for Beginners and More "
            "Experienced Players"
        ),
        license_name="Verify before redistribution",
        source_url="https://archive.org/details/dli.ministry.13269",
        download_url=(
            "https://archive.org/stream/dli.ministry.13269/"
            "E05421_The_Game_Of_Chess_djvu.txt"
        ),
        filename="dli_ministry_13269_the_game_of_chess.txt",
        notes="Internet Archive full text generated from OCR.",
    ),
]
