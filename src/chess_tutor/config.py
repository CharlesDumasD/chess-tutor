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
    processed_dir: str = "data/processed"
    chroma_collection_name: str = "chess_corpus"
    chunk_size: int = 1024
    chunk_overlap: int = 128
    embedding_cost_per_1m_tokens_usd: float = 0.02
    max_embedding_cost_usd: float = 0.50


def load_settings() -> Settings:
    """Load local environment variables and return application settings."""

    load_dotenv()

    return Settings(
        openai_api_key=getenv("OPENAI_API_KEY"),
        llm_model=getenv("OPENAI_LLM_MODEL", "gpt-4.1-mini"),
        embedding_model=getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        persist_dir=getenv("CHROMA_PERSIST_DIR", "data/generated/chroma_db"),
        processed_dir=getenv("PROCESSED_DATA_DIR", "data/processed"),
        chroma_collection_name=getenv("CHROMA_COLLECTION_NAME", "chess_corpus"),
        chunk_size=int(getenv("CHUNK_SIZE", "1024")),
        chunk_overlap=int(getenv("CHUNK_OVERLAP", "128")),
        embedding_cost_per_1m_tokens_usd=float(
            getenv("EMBEDDING_COST_PER_1M_TOKENS_USD", "0.02")
        ),
        max_embedding_cost_usd=float(getenv("MAX_EMBEDDING_COST_USD", "0.50")),
    )
