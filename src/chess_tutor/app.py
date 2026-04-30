"""Minimal Gradio entry point for the chess tutor."""

from pathlib import Path

import gradio as gr
from huggingface_hub import snapshot_download

from chess_tutor.config import load_settings
from chess_tutor.rag.engine import stream_answer

VECTOR_STORE_REPO_ID = "CharlesDumas/chess_tutor_vector_store"


def download_vector_store_if_missing() -> None:
    """Download the ChromaDB vector store from Hugging Face if needed."""

    settings = load_settings()
    persist_dir = Path(settings.persist_dir)
    chroma_file = persist_dir / "chroma.sqlite3"

    if chroma_file.exists():
        return

    persist_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=VECTOR_STORE_REPO_ID,
        repo_type="dataset",
        local_dir=persist_dir,
    )


def respond(question: str, history: list[dict[str, str]], api_key: str):
    """Stream an answer and update the visible chat history."""

    history = history or []

    if not question.strip():
        yield history, ""
        return

    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": ""},
    ]
    yield history, ""

    try:
        for partial_answer in stream_answer(question, api_key, history[:-2]):
            history[-1]["content"] = partial_answer
            yield history, ""
    except Exception as error:
        history[-1]["content"] = f"Something went wrong: {error}"
        yield history, ""


def build_chatbot() -> gr.Chatbot:
    """Build a chatbot compatible with local and Hugging Face Gradio versions."""

    try:
        return gr.Chatbot(label="Conversation", type="messages")
    except TypeError:
        return gr.Chatbot(label="Conversation")


def build_demo() -> gr.Blocks:
    """Build the Hugging Face Spaces-compatible Gradio interface."""

    download_vector_store_if_missing()
    with gr.Blocks(title="Chess Tutor") as demo:
        gr.Markdown("# Chess Tutor")
        gr.Markdown(
            "Ask a strategic chess question and get a sourced answer from a "
            "curated chess corpus."
        )

        api_key = gr.Textbox(
            label="OpenAI API key",
            type="password",
            placeholder="sk-...",
            info=(
                "Used only to call OpenAI for your current chat session; "
                "not stored by this app."
            ),
        )
        chatbot = build_chatbot()
        question = gr.Textbox(
            label="Question",
            lines=4,
            placeholder=(
                "What do you recommend me to play in the classical line of the "
                "Caro-Kann after 4... Nf6 5. Nxf6+ exf6? What are the key "
                "concepts here?"
            ),
        )
        submit = gr.Button("Ask")
        clear = gr.Button("Clear")

        submit.click(
            respond,
            inputs=[question, chatbot, api_key],
            outputs=[chatbot, question],
        )
        question.submit(
            respond,
            inputs=[question, chatbot, api_key],
            outputs=[chatbot, question],
        )
        clear.click(lambda: [], outputs=chatbot)

    return demo


def main() -> None:
    """Launch the local Gradio app."""

    build_demo().launch()


if __name__ == "__main__":
    main()
