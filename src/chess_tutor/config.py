"""Configuration helpers for the chess tutor app."""

from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    openai_api_key: str | None
    llm_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    persist_dir: str = "data/generated/chroma_db"


def load_settings() -> Settings:
    """Load local environment variables and return application settings."""

    load_dotenv()

    return Settings(
        openai_api_key=getenv("OPENAI_API_KEY"),
        llm_model=getenv("OPENAI_LLM_MODEL", "gpt-4.1-mini"),
        embedding_model=getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        persist_dir=getenv("CHROMA_PERSIST_DIR", "data/generated/chroma_db"),
    )
