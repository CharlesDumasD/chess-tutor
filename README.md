# Chess Tutor

A RAG-powered chess tutor for a GenAI engineering certification project.

The goal is to build an educational assistant that answers strategic chess
questions from a curated chess corpus and cites the retrieved sources used in
the answer. The app will use Python, LlamaIndex, ChromaDB, OpenAI LLMs and
embeddings, and a Gradio interface deployable on a public Hugging Face Space.

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

Optional: install pre-commit hooks.

```bash
uv run pre-commit install
```

## Pipeline 1: Data Collection

Download the raw corpus:

```bash
uv run chess-tutor-download
```

This downloads:

- 6 Project Gutenberg chess books
- 3 Internet Archive OCR text books
- 107 curated Wikipedia chess articles

Raw files are written to:

```text
data/raw/
```

Raw data is ignored by git. The downloader also writes provider-level metadata
files with source URLs, licenses, local paths, collection timestamps, and any
download errors.

## Pipeline 2: Text Processing

Status: not implemented yet.

This step will clean the raw text files and write normalized files to:

```text
data/processed/
```

Expected processing:

- Remove Project Gutenberg header/footer boilerplate
- Clean obvious Internet Archive OCR artifacts
- Keep Wikipedia text mostly as-is
- Preserve source metadata for later citations

## Pipeline 3: Vector Indexing

Status: not implemented yet.

This step will chunk the processed corpus, embed chunks with OpenAI embeddings,
and store them in ChromaDB.

Generated artifacts will be written to:

```text
data/generated/
```

The planned command is:

```bash
uv run chess-tutor-index
```

## Pipeline 4: RAG Tutor App

Status: placeholder UI implemented; RAG engine not connected yet.

Run the local Gradio app:

```bash
uv run chess-tutor
```

The final app will:

- Let the user paste an OpenAI API key
- Retrieve relevant chess corpus chunks from ChromaDB
- Generate a sourced answer with an OpenAI LLM through LlamaIndex
- Cite the source documents used in the answer

## Pipeline 5: Evaluation

Status: not implemented yet.

The planned command is:

```bash
uv run chess-tutor-evaluate
```

The evaluation pipeline will use a small golden dataset in:

```text
data/eval/
```

Planned evaluation:

- Retrieval checks against expected source evidence
- Generation checks for faithfulness, usefulness, and citation quality

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

## Codebase Structure

```text
src/chess_tutor/
  app.py                 Gradio UI entry point
  config.py              Environment and runtime settings
  data_collection/       Raw corpus download pipeline
  processing/            Text cleaning and normalization
  vector_store/          OpenAI embeddings and ChromaDB indexing
  rag/                   Prompting, retrieval, generation, and memory
  evaluation/            Golden dataset, retrieval metrics, generation metrics
data/
  README.md              Data layout and source rules
  raw/                   Downloaded source files (git ignored)
  processed/             Cleaned text files (git ignored)
  generated/             Chunks, vector stores, and logs (git ignored)
  eval/                  Golden datasets and evaluation reports (git tracked)
```

Note: only public domain or properly licensed sources should be included in the
repository. Copyrighted books should not be copied into the corpus unless their
license explicitly allows it.
