"""Minimal Gradio entry point for the chess tutor."""

import gradio as gr

from chess_tutor.config import load_settings


def answer_question(question: str, api_key: str) -> str:
    """Return a placeholder answer until the RAG pipeline is implemented."""

    if not api_key.strip():
        return "Please paste your OpenAI API key before asking a question."

    if not question.strip():
        return "Ask a chess strategy question to get started."

    return (
        "The RAG pipeline is not connected yet. Next steps are to ingest a public "
        "domain chess corpus into ChromaDB, retrieve relevant passages with "
        "LlamaIndex, and answer with OpenAI while citing sources."
    )


def build_demo() -> gr.Blocks:
    """Build the Hugging Face Spaces-compatible Gradio interface."""

    settings = load_settings()

    with gr.Blocks(title="Chess Tutor") as demo:
        gr.Markdown("# Chess Tutor")
        gr.Markdown(
            "Ask a strategic chess question and get a sourced answer from a "
            "curated chess corpus."
        )

        api_key = gr.Textbox(
            label="OpenAI API key",
            type="password",
            value=settings.openai_api_key or "",
            placeholder="sk-...",
        )
        question = gr.Textbox(
            label="Question",
            lines=4,
            placeholder="Why is the Nimzo-Indian pawn structure comfortable for Black?",
        )
        answer = gr.Markdown(label="Answer")
        submit = gr.Button("Ask")

        submit.click(answer_question, inputs=[question, api_key], outputs=answer)

    return demo


def main() -> None:
    """Launch the local Gradio app."""

    build_demo().launch()


if __name__ == "__main__":
    main()
