"""RAG engine wiring retrieval, prompting, and generation."""

from pathlib import Path

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from chess_tutor.config import load_settings
from chess_tutor.rag.prompts import CHESS_TUTOR_SYSTEM_PROMPT

ChatHistory = list[dict[str, str]]


def load_retriever(api_key: str):
    """Load the ChromaDB retriever from the persisted vector store."""

    settings = load_settings()
    persist_dir = Path(settings.persist_dir)

    if not persist_dir.exists():
        raise RuntimeError(
            f"ChromaDB index not found at {persist_dir}. "
            "Run `uv run chess-tutor-index` first."
        )

    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_collection(settings.chroma_collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=api_key,
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index.as_retriever(similarity_top_k=settings.similarity_top_k)


def format_context(retrieved_nodes) -> str:
    """Format retrieved chunks for the LLM prompt."""

    context_parts = []

    for index, result in enumerate(retrieved_nodes, start=1):
        metadata = result.node.metadata
        title = metadata.get("title", "Untitled source")
        source_url = metadata.get("source_url", "")
        text = result.node.get_content()

        context_parts.append(
            f"[{index}] {title}\n" f"Source: {source_url}\n" f"Text:\n{text}"
        )

    return "\n\n".join(context_parts)


def format_history(history: ChatHistory) -> str:
    """Format recent conversation history for follow-up questions."""

    settings = load_settings()
    recent_history = history[-settings.max_history_messages :]

    if not recent_history:
        return "No previous messages."

    lines = []
    for message in recent_history:
        role = message.get("role", "user")
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def format_sources(retrieved_nodes) -> str:
    """Format retrieved source list for display after the answer."""

    lines = ["\n\nSources:"]

    for index, result in enumerate(retrieved_nodes, start=1):
        metadata = result.node.metadata
        title = metadata.get("title", "Untitled source")
        source_url = metadata.get("source_url", "")

        if source_url:
            lines.append(f"[{index}] {title}: {source_url}")
        else:
            lines.append(f"[{index}] {title}")

    return "\n".join(lines)


def answer_question(
    question: str,
    api_key: str,
    history: ChatHistory | None = None,
) -> str:
    """Answer a chess question using the RAG pipeline."""

    settings = load_settings()
    history = history or []

    if not api_key.strip():
        return "Please paste your OpenAI API key before asking a question."

    if not question.strip():
        return "Ask a chess strategy question to get started."

    retriever = load_retriever(api_key)
    retrieved_nodes = retriever.retrieve(question)
    context = format_context(retrieved_nodes)
    conversation_history = format_history(history)

    user_prompt = f"""\
Conversation history:
{conversation_history}

Retrieved sources:
{context}

User question:
{question}
"""

    llm = OpenAI(
        model=settings.llm_model,
        api_key=api_key,
        temperature=settings.llm_temperature,
    )
    response = llm.chat(
        [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=CHESS_TUTOR_SYSTEM_PROMPT,
            ),
            ChatMessage(role=MessageRole.USER, content=user_prompt),
        ]
    )

    return (response.message.content or "") + format_sources(retrieved_nodes)
