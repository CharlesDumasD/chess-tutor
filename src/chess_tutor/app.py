"""Minimal Gradio entry point for the chess tutor."""

import gradio as gr

from chess_tutor.rag.engine import answer_question


def respond(question: str, history: list[dict[str, str]], api_key: str):
    """Answer a question and update the visible chat history."""

    history = history or []

    if not question.strip():
        return history, ""

    try:
        answer = answer_question(question, api_key, history)
    except Exception as error:
        answer = f"Something went wrong: {error}"

    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    return history, ""


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
