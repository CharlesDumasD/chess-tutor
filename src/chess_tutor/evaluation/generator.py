"""Evaluate generated answers with LlamaIndex evaluators."""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from llama_index.llms.openai import OpenAI

from chess_tutor.config import load_settings
from chess_tutor.evaluation.retriever import load_golden_dataset
from chess_tutor.rag.engine import generate_answer


def sample_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sample eval records so generator evaluation stays lightweight."""

    settings = load_settings()
    sample_size = min(settings.eval_generator_sample_size, len(records))
    rng = random.Random(settings.eval_random_seed)

    return rng.sample(records, sample_size)


def get_contexts(retrieved_nodes) -> list[str]:
    """Extract retrieved context strings from LlamaIndex nodes."""

    return [retrieved_node.node.get_content() for retrieved_node in retrieved_nodes]


def save_run_summary(summary: dict[str, object]) -> Path:
    """Save a timestamped generator evaluation summary."""

    settings = load_settings()
    runs_dir = Path(settings.eval_runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_path = runs_dir / f"generator_eval_{timestamp}.json"
    run_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return run_path


def evaluate_generator() -> None:
    """Evaluate answer faithfulness and relevancy for the current RAG pipeline."""

    settings = load_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to evaluate the generator.")

    dataset = sample_records(load_golden_dataset())
    judge_llm = OpenAI(
        model=settings.eval_llm_model,
        api_key=settings.openai_api_key,
        temperature=0.0,
    )
    faithfulness_evaluator = FaithfulnessEvaluator(llm=judge_llm)
    relevancy_evaluator = RelevancyEvaluator(llm=judge_llm)

    faithfulness_scores = []
    relevancy_scores = []
    examples = []

    print(f"Questions: {len(dataset)}")
    print(f"Generator model: {settings.llm_model}")
    print(f"Evaluator model: {settings.eval_llm_model}")
    print(f"Hybrid search: {settings.use_hybrid_search}")
    print(f"Reranker: {settings.use_reranker}")

    for index, record in enumerate(dataset, start=1):
        question = record["question"]
        answer, retrieved_nodes = generate_answer(
            question=question,
            api_key=settings.openai_api_key,
        )
        contexts = get_contexts(retrieved_nodes)

        faithfulness = faithfulness_evaluator.evaluate(
            query=question,
            response=answer,
            contexts=contexts,
        )
        relevancy = relevancy_evaluator.evaluate(
            query=question,
            response=answer,
            contexts=contexts,
        )

        faithfulness_score = faithfulness.score or 0.0
        relevancy_score = relevancy.score or 0.0
        faithfulness_scores.append(faithfulness_score)
        relevancy_scores.append(relevancy_score)

        examples.append(
            {
                "question": question,
                "answer": answer,
                "faithfulness_score": faithfulness_score,
                "faithfulness_feedback": faithfulness.feedback,
                "relevancy_score": relevancy_score,
                "relevancy_feedback": relevancy.feedback,
                "retrieved_chunk_ids": [
                    retrieved_node.node.node_id for retrieved_node in retrieved_nodes
                ],
            }
        )

        print(
            f"[{index}/{len(dataset)}] "
            f"faithfulness={faithfulness_score:.0f} "
            f"relevancy={relevancy_score:.0f}: {question}"
        )

    faithfulness_mean = sum(faithfulness_scores) / len(faithfulness_scores)
    relevancy_mean = sum(relevancy_scores) / len(relevancy_scores)

    summary = {
        "metric": "generator_eval",
        "questions": len(dataset),
        "generator_model": settings.llm_model,
        "evaluator_model": settings.eval_llm_model,
        "use_hybrid_search": settings.use_hybrid_search,
        "use_reranker": settings.use_reranker,
        "faithfulness": faithfulness_mean,
        "relevancy": relevancy_mean,
        "examples": examples,
    }
    run_path = save_run_summary(summary)

    print("")
    print(f"Faithfulness: {faithfulness_mean:.3f}")
    print(f"Relevancy: {relevancy_mean:.3f}")
    print(f"Saved run summary: {run_path}")


def main() -> None:
    """CLI entry point."""

    evaluate_generator()
