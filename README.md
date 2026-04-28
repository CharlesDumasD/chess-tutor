# Chess Tutor

A simple RAG-powered chess tutor for a GenAI engineering certification project.

The goal is to build an educational assistant that answers strategic chess
questions from a curated chess corpus and cites the retrieved sources used in
the answer. The first version will use Python, LlamaIndex, ChromaDB, OpenAI LLMs
and embeddings, and a Gradio interface deployable on a public Hugging Face Space.

## Project Constraints

- RAG project written in Python
- At least one LLM
- Public Hugging Face Space deployment
- Data collection and curation code in this repository
- UI element where the user can paste their API key
- README documentation for API key setup and cost estimation
- Estimated demo usage cost below USD 0.50

## Setup

Install [uv](https://docs.astral.sh/uv/) if needed, then create the local
environment:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Run the local Gradio app:

```bash
uv run chess-tutor
```

## Development

Install pre-commit hooks:

```bash
uv run pre-commit install
```

Run formatting and linting manually:

```bash
uv run black .
uv run isort .
uv run flake8 .
```

## Cost Estimation

The project is designed for lightweight demo usage. A typical question should
use one embedding call for the query, a small number of retrieved chunks, and one
LLM response.

Approximate target budget for a short demo session:

- 10 to 20 user questions
- Small embedding model for retrieval
- Small OpenAI chat model for answer generation
- Expected cost: less than USD 0.50 for normal certification/demo usage

The exact cost depends on the selected OpenAI models, prompt length, retrieved
context size, and answer length. The implementation should keep prompts compact
and use a low-cost model by default.

## Planned V1

1. Collect public domain or openly licensed chess strategy material.
2. Curate and chunk the corpus by theme, such as tactics, strategy, endgames,
   and openings.
3. Embed the chunks with OpenAI embeddings.
4. Store and retrieve chunks with ChromaDB.
5. Generate sourced answers with LlamaIndex and an OpenAI LLM.
6. Expose the tutor through a Gradio UI on Hugging Face Spaces.

Note: only public domain or properly licensed sources should be included in the
repository. Copyrighted books should not be copied into the corpus unless their
license explicitly allows it.

## Codebase Structure

```text
src/chess_tutor/
  app.py                 Gradio UI entry point
  config.py              Environment and runtime settings
  data_collection/       Source manifest and download pipeline
  processing/            PDF/text extraction, cleaning, and chunking
  vector_store/          OpenAI embeddings and ChromaDB indexing
  rag/                   Prompting, retrieval, generation, and memory
  evaluation/            Golden dataset, retrieval metrics, generation metrics
data/
  README.md              Data layout and source rules
  raw/                   Downloaded source files (git ignored)
  processed/             Extracted and cleaned text (git ignored)
  generated/             Chunks, vector stores, and logs (git ignored)
  eval/                  Golden datasets and evaluation reports (git tracked)
```

Pipeline commands will be added as the implementation grows:

```bash
uv run chess-tutor-download
uv run chess-tutor-index
uv run chess-tutor-evaluate
```

Download the six Project Gutenberg books:

```bash
uv run chess-tutor-download
```
