---
title: Chess Tutor
emoji: ♟️
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "5.27.0"
app_file: app.py
pinned: false
---

# Chess Tutor

A RAG-powered chess tutor for a GenAI engineering certification project.

General-purpose chatbots are often unreliable at chess because they can
hallucinate concrete lines, misread positions, and give confident but unsourced
opening advice. This project uses retrieval-augmented generation to ground the
assistant in a curated chess corpus and cite the sources used in each answer.

The app is built with Python, LlamaIndex, ChromaDB, OpenAI models, and a Gradio
interface deployable on Hugging Face Spaces.

## Design

The tutor answers chess strategy, opening, tactic, and endgame questions from a
curated text corpus:

- 6 public-domain Project Gutenberg chess books
- 2 Internet Archive OCR chess books
- 107 curated Wikipedia chess articles

The data pipeline downloads raw text, cleans it into processed text files, chunks
the documents with LlamaIndex, embeds the chunks with OpenAI embeddings, and
stores them in a local ChromaDB vector store.

The RAG app retrieves relevant chunks, optionally combines semantic and keyword
retrieval with hybrid search, streams an answer from an OpenAI chat model, and
shows source citations. The UI includes a password field where users paste their
own OpenAI API key for the current chat session.

Final retrieval configuration:

- ChromaDB vector store with cosine similarity
- `text-embedding-3-small` embeddings
- Hybrid search enabled
- LLM reranking implemented but disabled by default because evaluation did not
  justify the additional latency and cost
- Top 10 chunks used as answer context

## Evaluation

The project includes an evaluation dataset and evaluation scripts in
`src/chess_tutor/evaluation/`.

The golden dataset is generated from indexed chunks and saved as JSONL in:

```text
data/eval/golden_dataset.jsonl
```

Retriever evaluation measures:

- Hit rate
- MRR

Generator evaluation measures:

- Faithfulness
- Relevancy

Current evaluation results:

| Configuration | Hit Rate |   MRR | Faithfulness | Relevancy |
| --- |---------:|------:|-------------:|----------:|
| Vector search baseline |    0.310 | 0.170 |        0.750 |     0.800 |
| Hybrid search |    0.300 | 0.161 |        0.800 |     0.850 |
| Hybrid search + reranking |    0.230 | 0.128 |            - |         - |

Hybrid search did not improve the chunk-level retrieval metrics on the generated
evaluation dataset. It is still enabled in the final app because chess questions
often contain exact opening names, tactical motifs, and move notation where
keyword matching is useful in practice. Reranking remains available through
configuration, but is disabled by default because it added latency and cost
without clear metric improvement.

## Implemented Optional Functionalities

The project implements at least 5 optional functionalities from the course list:

- Streaming responses in the Gradio chat UI
- RAG evaluation code, evaluation dataset, and evaluation results
- Specific non-AI domain: chess tutoring
- Evidence of collecting multiple external data sources: Project Gutenberg, Internet Archive, and Wikipedia
- Hybrid search combining vector retrieval and keyword retrieval
- LLM reranking implemented as an optional retrieval layer

## Required API Keys

To use the app, the user needs:

- OpenAI API key

For local development, place it in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

For the Gradio app, paste the OpenAI API key into the UI password field. The app
uses that key only for the current chat session; it does not write the key to
files, log it, or store it in conversation history.

## Cost Estimation

The app is designed so a user can try all main functionality for less than
USD 0.50 with their own OpenAI API key.

Approximate demo session:

- 10 to 20 chat questions
- one query embedding call per question
- one small OpenAI chat completion per answer
- 10 retrieved chunks in the answer context
- no indexing cost charged to the app user

The indexing pipeline uses `text-embedding-3-small`. In local testing, indexing
the full corpus was estimated at about 1.5M embedding tokens, or roughly USD
0.03 at USD 0.02 per 1M tokens. Normal app usage is cheaper because each user
question embeds only the query and sends one compact RAG prompt to the chat
model.

The exact cost depends on the selected OpenAI models, answer length, and number
of questions, but a normal certification/demo session should remain well below
USD 0.50.

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

Raw files are written to:

```text
data/raw/
```

Raw data is ignored by git. The downloader also writes provider-level metadata
files with source URLs, licenses, local paths, collection timestamps, and any
download errors.

## Pipeline 2: Text Processing

Clean raw text files into normalized processed text:

```bash
uv run chess-tutor-process
```

Processed files are written to:

```text
data/processed/
```

## Pipeline 3: Vector Indexing

Chunk the processed corpus, embed chunks with OpenAI embeddings, and store them
in ChromaDB:

```bash
uv run chess-tutor-index
```

Generated artifacts are written to:

```text
data/generated/
```

The index command rebuilds the local ChromaDB collection each time. Pipeline
settings are loaded from `src/chess_tutor/config.py`; defaults can be changed
there, while secrets and local overrides can be placed in `.env`.

## Pipeline 4: RAG Tutor App

Run the local Gradio app:

```bash
uv run chess-tutor
```

The Hugging Face Spaces entry point is the root `app.py`.

## Pipeline 5: Evaluation Dataset

Create the golden evaluation dataset:

```bash
uv run chess-tutor-generate-eval-dataset
```

If the dataset already exists, the command stops without regenerating it. This
keeps evaluation runs comparable and avoids unnecessary OpenAI API calls.

## Pipeline 6: Evaluation Metrics

Run retriever evaluation:

```bash
uv run chess-tutor-eval-retriever
```

Run generator evaluation:

```bash
uv run chess-tutor-eval-generator
```

Evaluation run summaries are written to:

```text
data/eval/runs/
```

## Codebase Structure

```text
app.py                  Hugging Face Spaces entry point
requirements.txt        Hugging Face Spaces Python install file
src/chess_tutor/
  app.py                Gradio UI
  config.py             Runtime settings
  data_collection/      Raw corpus download pipeline
  data_processing/      Text cleaning and normalization
  vector_store/         OpenAI embeddings and ChromaDB indexing
  rag/                  Prompting, retrieval, generation, and chat history
  evaluation/           Golden dataset, retrieval metrics, generation metrics
data/
  README.md             Data layout and source rules
  raw/                  Downloaded source files (git ignored)
  processed/            Cleaned text files (git ignored)
  generated/            ChromaDB vector store (git ignored)
  eval/                 Golden dataset and evaluation reports
```

Note: only public domain or properly licensed sources should be included in the
corpus. Copyrighted books should not be copied into the corpus unless their
license explicitly allows it.
