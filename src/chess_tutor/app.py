"""Minimal Gradio entry point for the chess tutor."""

import gradio as gr

from chess_tutor.rag.engine import stream_answer


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


def build_demo() -> gr.Blocks:
    """Build the Hugging Face Spaces-compatible Gradio interface."""

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
        chatbot = gr.Chatbot(label="Conversation")
        question = gr.Textbox(
            label="Question",
            lines=4,
            placeholder="Why is the Nimzo-Indian pawn structure comfortable for Black?",
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
