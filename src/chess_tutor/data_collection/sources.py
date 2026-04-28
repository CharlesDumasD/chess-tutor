"""Source metadata models for chess corpus collection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """A source document considered for the chess tutor corpus."""

    title: str
    author: str
    url: str
    license_name: str
    source_type: str
    notes: str = ""
