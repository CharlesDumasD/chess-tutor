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

The local `.env` key is used by backend pipeline commands such as indexing.
The Gradio app also includes a password field where users can paste their own
OpenAI API key. That UI key is passed to the backend only to call OpenAI for the
current chat session; the app does not log it, write it to files, or store it in
conversation history.

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

This step will clean the raw text files and write normalized files to:

```text
data/processed/
```

Processing includes:

- Remove Project Gutenberg header/footer boilerplate
- Normalize whitespace
- Keep Wikipedia text mostly as-is
- Preserve source metadata for later citations

Run the processing pipeline:

```bash
uv run chess-tutor-process
```

## Pipeline 3: Vector Indexing

This step will chunk the processed corpus, embed chunks with OpenAI embeddings,
and store them in ChromaDB.

Generated artifacts will be written to:

```text
data/generated/
```

Run the indexing pipeline:

```bash
uv run chess-tutor-index
```

The index command rebuilds the local ChromaDB collection each time using cosine
similarity, which keeps the pipeline simple and avoids duplicate chunks while
iterating.

Pipeline settings are loaded from `src/chess_tutor/config.py`. The `Settings`
dataclass defines the default values used by the app, including:

- embedding model
- LLM model
- processed data directory
- ChromaDB persist directory and collection name
- chunk size and overlap
- retrieval top-k
- conversation memory length
- LLM temperature
- embedding cost estimate and maximum allowed indexing cost

For experiments, change the defaults in `config.py`. For local secrets or
machine-specific overrides, add environment variables to `.env`; `load_settings()`
loads `.env` and lets environment variables override the defaults.

The default embedding cost estimate uses OpenAI's published
`text-embedding-3-small` price of USD 0.02 per 1M tokens.
If the estimated embedding cost is above `max_embedding_cost_usd`, the index
command stops before calling the OpenAI API. The default limit is USD 0.50.

## Pipeline 4: RAG Tutor App

Run the local Gradio app:

```bash
uv run chess-tutor
```

The final app will:

- Let the user paste an OpenAI API key
- Retrieve relevant chess corpus chunks from ChromaDB
- Generate a sourced answer with an OpenAI LLM through LlamaIndex
- Cite the source documents used in the answer
- Keep simple conversational memory through the Gradio chat history

## Pipeline 5: Evaluation Dataset

Create a small golden dataset of evaluation questions:

```bash
uv run chess-tutor-generate-eval-dataset
```

This command loads chunks from the current ChromaDB index and generates one
question for a small deterministic sample of chunks. The result is saved to:

```text
data/eval/golden_dataset.jsonl
```

If the dataset already exists, the command stops without regenerating it. This
keeps evaluation runs comparable and avoids unnecessary OpenAI API calls.

Evaluation settings are loaded from `config.py`:

- `eval_dataset_path`
- `eval_llm_model`
- `eval_runs_dir`
- `eval_sample_size`
- `eval_random_seed`
- `eval_wikipedia_sample_ratio`
- `eval_generator_sample_size`
- `use_hybrid_search`
- `hybrid_keyword_top_k`

## Pipeline 6: Evaluation Metrics

Run retriever evaluation:

```bash
uv run chess-tutor-eval-retriever
```

This computes hit rate and MRR by checking whether the retriever returns the
expected source chunk from the golden dataset.

Run generator evaluation:

```bash
uv run chess-tutor-eval-generator
```

This samples a smaller subset of the golden dataset, generates answers with the
current RAG pipeline, and scores them with LlamaIndex evaluators:

- Retrieval checks against expected source evidence with hit rate and MRR
- Generation checks for faithfulness and relevancy

Evaluation run summaries are written to:

```text
data/eval/runs/
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

## Codebase Structure

```text
src/chess_tutor/
  app.py                 Gradio UI entry point
  config.py              Environment and runtime settings
  data_collection/       Raw corpus download pipeline
  data_processing/       Text cleaning and normalization
  vector_store/          OpenAI embeddings and ChromaDB indexing
  rag/                   Prompting, retrieval, generation, and chat history
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
