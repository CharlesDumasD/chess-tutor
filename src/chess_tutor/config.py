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
    similarity_top_k: int = 5
    max_history_messages: int = 6
    llm_temperature: float = 0.2
    eval_dataset_path: str = "data/eval/golden_dataset.jsonl"
    eval_sample_size: int = 100
    eval_random_seed: int = 7


def load_settings() -> Settings:
    """Load local environment variables and return application settings."""

    load_dotenv()
    defaults = Settings(openai_api_key=None)

    return Settings(
        openai_api_key=getenv("OPENAI_API_KEY"),
        llm_model=getenv("OPENAI_LLM_MODEL", defaults.llm_model),
        embedding_model=getenv("OPENAI_EMBEDDING_MODEL", defaults.embedding_model),
        persist_dir=getenv("CHROMA_PERSIST_DIR", defaults.persist_dir),
        processed_dir=getenv("PROCESSED_DATA_DIR", defaults.processed_dir),
        chroma_collection_name=getenv(
            "CHROMA_COLLECTION_NAME", defaults.chroma_collection_name
        ),
        chunk_size=int(getenv("CHUNK_SIZE", str(defaults.chunk_size))),
        chunk_overlap=int(getenv("CHUNK_OVERLAP", str(defaults.chunk_overlap))),
        embedding_cost_per_1m_tokens_usd=float(
            getenv(
                "EMBEDDING_COST_PER_1M_TOKENS_USD",
                str(defaults.embedding_cost_per_1m_tokens_usd),
            )
        ),
        max_embedding_cost_usd=float(
            getenv("MAX_EMBEDDING_COST_USD", str(defaults.max_embedding_cost_usd))
        ),
        similarity_top_k=int(
            getenv("SIMILARITY_TOP_K", str(defaults.similarity_top_k))
        ),
        max_history_messages=int(
            getenv("MAX_HISTORY_MESSAGES", str(defaults.max_history_messages))
        ),
        llm_temperature=float(
            getenv("OPENAI_LLM_TEMPERATURE", str(defaults.llm_temperature))
        ),
        eval_dataset_path=getenv("EVAL_DATASET_PATH", defaults.eval_dataset_path),
        eval_sample_size=int(
            getenv("EVAL_SAMPLE_SIZE", str(defaults.eval_sample_size))
        ),
        eval_random_seed=int(
            getenv("EVAL_RANDOM_SEED", str(defaults.eval_random_seed))
        ),
    )
