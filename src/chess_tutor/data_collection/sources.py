"""Source metadata models for chess corpus collection."""

from dataclasses import dataclass
from urllib.parse import quote, urlencode


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
        download_url="https://www.gutenberg.org/cache/epub/33870/pg33870.txt",
        filename="33870_chess_fundamentals.txt",
    ),
    Source(
        source_id="5614",
        provider="project_gutenberg",
        author="Edward Lasker",
        title="Chess Strategy",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/5614",
        download_url="https://www.gutenberg.org/cache/epub/5614/pg5614.txt",
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
        download_url="https://www.gutenberg.org/cache/epub/4913/pg4913.txt",
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
        download_url="https://www.gutenberg.org/cache/epub/16377/pg16377.txt",
        filename="16377_blue_book_of_chess.txt",
    ),
    Source(
        source_id="4902",
        provider="project_gutenberg",
        author="H. E. Bird",
        title="Chess History and Reminiscences",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/4902",
        download_url="https://www.gutenberg.org/cache/epub/4902/pg4902.txt",
        filename="4902_chess_history_and_reminiscences.txt",
    ),
    Source(
        source_id="55278",
        provider="project_gutenberg",
        author="Franklin K. Young",
        title="Chess Generalship, Vol. I. Grand Reconnaissance",
        license_name="Public domain in the USA",
        source_url="https://www.gutenberg.org/ebooks/55278",
        download_url="https://www.gutenberg.org/cache/epub/55278/pg55278.txt",
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
            "https://archive.org/download/commonsenseinche00laskrich/"
            "commonsenseinche00laskrich_djvu.txt"
        ),
        filename="commonsenseinche00laskrich_common_sense_in_chess.txt",
        notes="Internet Archive full text generated from OCR.",
    ),
    Source(
        source_id="bwb_S0-CIH-670",
        provider="internet_archive",
        author="Emanuel Lasker",
        title="Lasker's Manual of Chess",
        license_name="Public domain",
        source_url=(
            "https://commons.wikimedia.org/wiki/"
            "File:Lasker_(1927)_-_Manual_of_Chess.pdf"
        ),
        download_url=(
            "https://archive.org/download/bwb_S0-CIH-670/" "bwb_S0-CIH-670_djvu.txt"
        ),
        filename="bwb_s0_cih_670_laskers_manual_of_chess.txt",
        notes="Wikimedia Commons public-domain PDF; text from Internet Archive OCR.",
    ),
]


WIKIPEDIA_ARTICLE_TITLES = {
    "core": [
        "Chess",
        "Rules of chess",
        "Chess notation",
        "Algebraic notation (chess)",
        "Forsyth–Edwards Notation",
        "Chess title",
        "Elo rating system",
        "Chess clock",
        "Time control",
        "Draw (chess)",
        "Checkmate",
        "Stalemate",
        "Castling",
        "Promotion (chess)",
        "En passant",
    ],
    "strategy": [
        "Chess strategy",
        "Pawn structure",
        "Isolated pawn",
        "Doubled pawns",
        "Backward pawn",
        "Passed pawn",
        "Pawn majority",
        "Pawn chain",
        "Hanging pawns",
        "Minority attack",
        "Open file",
        "Half-open file",
        "Outpost (chess)",
        "Space (chess)",
        "Tempo (chess)",
        "Initiative (chess)",
        "Prophylaxis (chess)",
        "Zugzwang",
        "Fianchetto",
        "Center (chess)",
    ],
    "tactics": [
        "Chess tactic",
        "Fork (chess)",
        "Pin (chess)",
        "Skewer (chess)",
        "Discovered attack",
        "Discovered check",
        "Double check",
        "Battery (chess)",
        "Deflection (chess)",
        "Decoy (chess)",
        "Interference (chess)",
        "Overloading (chess)",
        "X-ray (chess)",
        "Windmill (chess)",
        "Clearance sacrifice",
        "Sacrifice (chess)",
        "Combination (chess)",
        "Zwischenzug",
        "Perpetual check",
    ],
    "endgames": [
        "Chess endgame",
        "Pawnless chess endgame",
        "King and pawn versus king endgame",
        "Opposition (chess)",
        "Key square",
        "Lucena position",
        "Philidor position",
        "Rook and pawn versus rook endgame",
        "Queen versus pawn endgame",
        "Wrong rook pawn",
        "Triangulation (chess)",
        "Fortress (chess)",
        "Endgame tablebase",
        "Fifty-move rule",
        "Threefold repetition",
    ],
    "openings": [
        "Chess opening",
        "List of chess openings",
        "Open Game",
        "Semi-Open Game",
        "Closed Game",
        "Semi-Closed Game",
        "Flank opening",
        "King's Pawn Game",
        "Queen's Pawn Game",
        "Sicilian Defence",
        "French Defence",
        "Caro-Kann Defence",
        "Pirc Defence",
        "Modern Defense",
        "Alekhine's Defence",
        "Scandinavian Defense",
        "Ruy Lopez",
        "Italian Game",
        "Scotch Game",
        "Four Knights Game",
        "Petrov's Defence",
        "King's Gambit",
        "Queen's Gambit",
        "Queen's Gambit Accepted",
        "Queen's Gambit Declined",
        "Slav Defense",
        "Semi-Slav Defense",
        "Nimzo-Indian Defence",
        "Queen's Indian Defense",
        "King's Indian Defence",
        "Grünfeld Defence",
        "Benoni Defense",
        "Dutch Defence",
        "English Opening",
        "Réti Opening",
        "Catalan Opening",
        "London System",
        "King's Indian Attack",
    ],
}


def wikipedia_filename(title: str) -> str:
    """Return a stable local filename for a Wikipedia article title."""

    filename = title.lower()
    filename = filename.replace("'", "")
    filename = filename.replace("(", "")
    filename = filename.replace(")", "")
    filename = filename.replace("-", "_")
    filename = filename.replace(" ", "_")
    return f"{filename}.txt"


def build_wikipedia_sources() -> list[Source]:
    """Build Source objects from the curated Wikipedia article titles."""

    sources = []

    for theme, titles in WIKIPEDIA_ARTICLE_TITLES.items():
        for title in titles:
            encoded_title = quote(title.replace(" ", "_"), safe="")
            query = urlencode(
                {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "explaintext": "1",
                    "redirects": "1",
                    "titles": title,
                }
            )
            sources.append(
                Source(
                    source_id=title,
                    provider="wikipedia",
                    author="Wikipedia contributors",
                    title=title,
                    license_name="CC BY-SA 4.0",
                    source_url=f"https://en.wikipedia.org/wiki/{encoded_title}",
                    download_url=f"https://en.wikipedia.org/w/api.php?{query}",
                    filename=wikipedia_filename(title),
                    notes=f"Curated Wikipedia article for theme: {theme}.",
                )
            )

    return sources


WIKIPEDIA_SOURCES = build_wikipedia_sources()
