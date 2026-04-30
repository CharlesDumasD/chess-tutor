"""Create a small golden dataset for retrieval and generation evaluation."""

import json
import random
from collections import Counter
from pathlib import Path

import chromadb
from llama_index.llms.openai import OpenAI

from chess_tutor.config import load_settings


def build_question_prompt(chunk_text: str, title: str) -> str:
    """Build the prompt used to create one evaluation question."""

    excerpt = chunk_text[:2500]

    return f"""
You are creating an evaluation question for a chess RAG tutor.

Write one natural question that a chess student might ask a tutor.
The question must be about a reusable chess concept, plan, opening idea,
tactical motif, endgame idea, or positional theme found in the source chunk.

Good questions sound like:
- "Why can an isolated pawn become weak in the endgame?"
- "What is Black trying to achieve in Alekhine's Defence?"
- "How should I think about outposts created by backward pawns?"

Avoid questions about the document itself.
Do not ask what the text says, what examples are mentioned, what game number is
shown, who played a specific historical game, or what the exact first moves were.
Do not mention the source title or say "according to the text".

Return only valid JSON with this shape:
{{"question": "..."}}

Source title: {title}

Source chunk:
{excerpt}
""".strip()


def parse_question(raw_response: str) -> str:
    """Parse a generated question from the LLM response."""

    cleaned = raw_response.strip()
    cleaned = cleaned.removeprefix("```json").removeprefix("```")
    cleaned = cleaned.removesuffix("```").strip()

    data = json.loads(cleaned)
    question = data["question"].strip()

    if not question:
        raise ValueError("Generated question is empty.")

    return question


def load_index_chunks() -> list[dict[str, object]]:
    """Load indexed chunks from the local ChromaDB collection."""

    settings = load_settings()
    chroma_client = chromadb.PersistentClient(path=settings.persist_dir)
    collection = chroma_client.get_collection(settings.chroma_collection_name)
    records = collection.get(include=["documents", "metadatas"])

    chunks = []

    for chunk_id, document, metadata in zip(
        records["ids"],
        records["documents"],
        records["metadatas"],
    ):
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata or {},
            }
        )

    return chunks


def sample_chunks(chunks: list[dict[str, object]]) -> list[dict[str, object]]:
    """Sample chunks with a minimum share of Wikipedia articles."""

    settings = load_settings()
    sample_size = min(settings.eval_sample_size, len(chunks))
    rng = random.Random(settings.eval_random_seed)

    wikipedia_chunks = [
        chunk for chunk in chunks if chunk["metadata"].get("provider") == "wikipedia"
    ]
    other_chunks = [
        chunk for chunk in chunks if chunk["metadata"].get("provider") != "wikipedia"
    ]

    wikipedia_sample_size = min(
        round(sample_size * settings.eval_wikipedia_sample_ratio),
        len(wikipedia_chunks),
    )
    other_sample_size = min(sample_size - wikipedia_sample_size, len(other_chunks))

    sampled_chunks = []
    sampled_chunks.extend(rng.sample(wikipedia_chunks, wikipedia_sample_size))
    sampled_chunks.extend(rng.sample(other_chunks, other_sample_size))

    remaining_sample_size = sample_size - len(sampled_chunks)
    if remaining_sample_size:
        already_sampled_ids = {chunk["chunk_id"] for chunk in sampled_chunks}
        remaining_chunks = [
            chunk for chunk in chunks if chunk["chunk_id"] not in already_sampled_ids
        ]
        sampled_chunks.extend(rng.sample(remaining_chunks, remaining_sample_size))

    rng.shuffle(sampled_chunks)
    return sampled_chunks


def build_golden_dataset() -> None:
    """Build a reusable JSONL file of generated eval questions."""

    settings = load_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate eval questions.")

    dataset_path = Path(settings.eval_dataset_path)

    if dataset_path.exists():
        print(f"Golden dataset already exists: {dataset_path}")
        print("Delete it if you want to regenerate it.")
        return

    chunks = load_index_chunks()

    if not chunks:
        raise RuntimeError("No chunks found in ChromaDB. Run chess-tutor-index first.")

    sampled_chunks = sample_chunks(chunks)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = dataset_path.with_suffix(f"{dataset_path.suffix}.tmp")

    llm = OpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )

    print(f"Loaded indexed chunks: {len(chunks)}")
    print(f"Questions to generate: {len(sampled_chunks)}")
    sampled_providers = Counter(
        chunk["metadata"].get("provider") for chunk in sampled_chunks
    )
    print(f"Sampled providers: {dict(sampled_providers)}")
    print(f"Output file: {dataset_path}")

    try:
        with temporary_path.open("w", encoding="utf-8") as output_file:
            for index, chunk in enumerate(sampled_chunks, start=1):
                metadata = chunk["metadata"]
                title = metadata.get("title", "")
                source_url = metadata.get("source_url", "")
                chunk_text = chunk["text"]

                response = llm.complete(build_question_prompt(chunk_text, title))
                question = parse_question(str(response))

                record = {
                    "question": question,
                    "reference_chunk_id": chunk["chunk_id"],
                    "reference_context": chunk_text,
                    "title": title,
                    "source_url": source_url,
                    "provider": metadata.get("provider", ""),
                }

                output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"[{index}/{len(sampled_chunks)}] {question}")
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    temporary_path.replace(dataset_path)
    print(f"Saved golden dataset: {dataset_path}")


def main() -> None:
    """CLI entry point."""

    build_golden_dataset()
