# Data Directory

This project separates downloaded source files, processed text, generated
artifacts, and evaluation data so the RAG pipeline stays easy to inspect.

## Suggested Layout

- `raw/`: downloaded source files such as PDFs, HTML, or text exports.
- `processed/`: extracted and cleaned text files.
- `generated/`: generated chunks, vector stores, logs, and intermediate artifacts.
- `eval/`: golden datasets and evaluation reports.

`raw/`, `processed/`, and `generated/` are ignored by git because they should be
reproducible from the pipeline. `eval/` is tracked for small golden datasets and
human-reviewed evaluation files.

## Source Rules

- Prefer public domain or openly licensed chess material.
- Record source URL, title, author, license, and retrieval date.
- Do not commit copyrighted book text unless the license explicitly allows it.
