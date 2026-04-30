"""Evaluate whether the retriever finds the expected source chunks."""

import json
from datetime import datetime, timezone
from pathlib import Path

from chess_tutor.config import load_settings
from chess_tutor.rag.engine import retrieve_nodes


def load_golden_dataset() -> list[dict[str, str]]:
    """Load the saved golden dataset."""

    settings = load_settings()
    dataset_path = Path(settings.eval_dataset_path)

    if not dataset_path.exists():
        raise RuntimeError(
            f"Golden dataset not found at {dataset_path}. "
            "Run `uv run chess-tutor-generate-eval-dataset` first."
        )

    records = []

    with dataset_path.open(encoding="utf-8") as dataset_file:
        for line in dataset_file:
            records.append(json.loads(line))

    return records


def get_node_id(retrieved_node) -> str:
    """Get the stable node id from a LlamaIndex retrieval result."""

    return retrieved_node.node.node_id


def reciprocal_rank(retrieved_ids: list[str], expected_id: str) -> float:
    """Return reciprocal rank for one query."""

    for rank, retrieved_id in enumerate(retrieved_ids, start=1):
        if retrieved_id == expected_id:
            return 1 / rank

    return 0.0


def save_run_summary(summary: dict[str, object]) -> Path:
    """Save a timestamped evaluation summary."""

    settings = load_settings()
    runs_dir = Path(settings.eval_runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_path = runs_dir / f"retriever_eval_{timestamp}.json"
    run_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return run_path


def evaluate_retriever() -> None:
    """Compute hit rate and MRR for the current retriever."""

    settings = load_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to evaluate the retriever.")

    dataset = load_golden_dataset()
    hits = 0
    reciprocal_ranks = []
    examples = []

    print(f"Questions: {len(dataset)}")
    print(f"Retriever top-k: {settings.similarity_top_k}")
    print(f"Hybrid search: {settings.use_hybrid_search}")
    print(f"Reranker: {settings.use_reranker}")
    print(f"Vector candidate top-k: {settings.vector_candidate_top_k}")
    print(f"Keyword candidate top-k: {settings.hybrid_keyword_top_k}")

    for index, record in enumerate(dataset, start=1):
        question = record["question"]
        expected_id = record["reference_chunk_id"]
        retrieved_nodes = retrieve_nodes(question, settings.openai_api_key)
        retrieved_ids = [get_node_id(node) for node in retrieved_nodes]

        hit = expected_id in retrieved_ids
        rank_score = reciprocal_rank(retrieved_ids, expected_id)

        hits += int(hit)
        reciprocal_ranks.append(rank_score)

        examples.append(
            {
                "question": question,
                "expected_chunk_id": expected_id,
                "retrieved_chunk_ids": retrieved_ids,
                "hit": hit,
                "reciprocal_rank": rank_score,
            }
        )

        status = "hit" if hit else "miss"
        print(f"[{index}/{len(dataset)}] {status}: {question}")

    hit_rate = hits / len(dataset)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    summary = {
        "metric": "retriever_eval",
        "questions": len(dataset),
        "top_k": settings.similarity_top_k,
        "use_hybrid_search": settings.use_hybrid_search,
        "use_reranker": settings.use_reranker,
        "vector_candidate_top_k": settings.vector_candidate_top_k,
        "hybrid_keyword_top_k": settings.hybrid_keyword_top_k,
        "hit_rate": hit_rate,
        "mrr": mrr,
        "examples": examples,
    }
    run_path = save_run_summary(summary)

    print("")
    print(f"Hit rate: {hit_rate:.3f}")
    print(f"MRR: {mrr:.3f}")
    print(f"Saved run summary: {run_path}")


def main() -> None:
    """CLI entry point."""

    evaluate_retriever()
