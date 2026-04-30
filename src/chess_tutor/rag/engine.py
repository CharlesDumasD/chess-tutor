"""RAG engine wiring retrieval, prompting, and generation."""

from collections.abc import Generator
from pathlib import Path

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.indices.keyword_table import SimpleKeywordTableIndex
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from chess_tutor.config import load_settings
from chess_tutor.rag.prompts import CHESS_TUTOR_SYSTEM_PROMPT

ChatHistory = list[dict[str, str]]


class HybridRetriever(BaseRetriever):
    """Retriever that combines semantic search and simple keyword search."""

    def __init__(
        self,
        vector_retriever: BaseRetriever,
        keyword_retriever: BaseRetriever,
        max_retrieve: int,
    ) -> None:
        """Initialize the hybrid retriever."""

        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.max_retrieve = max_retrieve
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Retrieve nodes from both retrievers and deduplicate by node id."""

        vector_nodes = self.vector_retriever.retrieve(query_bundle)
        keyword_nodes = self.keyword_retriever.retrieve(query_bundle)
        results = []
        seen_node_ids = set()

        for nodes in zip(vector_nodes, keyword_nodes):
            for node in nodes:
                if node.node.node_id in seen_node_ids:
                    continue

                results.append(node)
                seen_node_ids.add(node.node.node_id)

                if len(results) >= self.max_retrieve:
                    return results

        for node in vector_nodes + keyword_nodes:
            if node.node.node_id in seen_node_ids:
                continue

            results.append(node)
            seen_node_ids.add(node.node.node_id)

            if len(results) >= self.max_retrieve:
                return results

        return results


def load_chroma_collection():
    """Load the configured ChromaDB collection."""

    settings = load_settings()
    persist_dir = Path(settings.persist_dir)

    if not persist_dir.exists():
        raise RuntimeError(
            f"ChromaDB index not found at {persist_dir}. "
            "Run `uv run chess-tutor-index` first."
        )

    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    return chroma_client.get_collection(settings.chroma_collection_name)


def load_keyword_retriever(chroma_collection):
    """Build a simple keyword retriever from persisted Chroma chunks."""

    settings = load_settings()
    records = chroma_collection.get(include=["documents", "metadatas"])
    nodes = []

    for chunk_id, document, metadata in zip(
        records["ids"],
        records["documents"],
        records["metadatas"],
    ):
        nodes.append(
            TextNode(
                id_=chunk_id,
                text=document,
                metadata=metadata or {},
            )
        )

    keyword_index = SimpleKeywordTableIndex(nodes=nodes)
    return keyword_index.as_retriever(
        retriever_mode="simple",
        num_chunks_per_query=settings.hybrid_keyword_top_k,
    )


def load_retriever(api_key: str):
    """Load the ChromaDB retriever from the persisted vector store."""

    settings = load_settings()
    candidate_top_k = (
        settings.vector_candidate_top_k
        if settings.use_reranker
        else settings.similarity_top_k
    )
    chroma_collection = load_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=api_key,
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    vector_retriever = index.as_retriever(similarity_top_k=candidate_top_k)

    if not settings.use_hybrid_search:
        return vector_retriever

    keyword_retriever = load_keyword_retriever(chroma_collection)
    return HybridRetriever(
        vector_retriever=vector_retriever,
        keyword_retriever=keyword_retriever,
        max_retrieve=candidate_top_k,
    )


def rerank_nodes(question: str, api_key: str, retrieved_nodes):
    """Rerank retrieved chunks and keep the final top-k."""

    settings = load_settings()

    if not settings.use_reranker:
        return retrieved_nodes[: settings.similarity_top_k]

    reranker_llm = OpenAI(
        model=settings.eval_llm_model,
        api_key=api_key,
        temperature=0.0,
    )
    reranker = LLMRerank(
        llm=reranker_llm,
        top_n=settings.similarity_top_k,
    )

    return reranker.postprocess_nodes(retrieved_nodes, query_str=question)


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


def build_retrieval_query(question: str, history: ChatHistory) -> str:
    """Build a retrieval query that includes recent conversation context."""

    conversation_history = format_history(history)

    if conversation_history == "No previous messages.":
        return question

    return f"""\
Recent conversation:
{conversation_history}

Current question:
{question}
"""


def retrieve_nodes(question: str, api_key: str, history: ChatHistory | None = None):
    """Retrieve relevant chunks for a question."""

    history = history or []
    retriever = load_retriever(api_key)
    retrieval_query = build_retrieval_query(question, history)

    retrieved_nodes = retriever.retrieve(retrieval_query)
    return rerank_nodes(retrieval_query, api_key, retrieved_nodes)


def build_user_prompt(
    question: str,
    retrieved_nodes,
    history: ChatHistory | None = None,
) -> str:
    """Build the user prompt for answer generation."""

    history = history or []
    context = format_context(retrieved_nodes)
    conversation_history = format_history(history)

    return f"""\
Conversation history:
{conversation_history}

Retrieved sources:
{context}

User question:
{question}
"""


def build_messages(user_prompt: str) -> list[ChatMessage]:
    """Build chat messages for the chess tutor LLM."""

    return [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=CHESS_TUTOR_SYSTEM_PROMPT,
        ),
        ChatMessage(role=MessageRole.USER, content=user_prompt),
    ]


def format_sources(retrieved_nodes) -> str:
    """Format a deduplicated source list for display after the answer."""

    lines = ["\n\nSources:"]
    sources = {}

    for index, result in enumerate(retrieved_nodes, start=1):
        metadata = result.node.metadata
        title = metadata.get("title", "Untitled source")
        source_url = metadata.get("source_url", "")
        source_key = source_url or title

        if source_key not in sources:
            sources[source_key] = {
                "title": title,
                "source_url": source_url,
                "chunk_numbers": [],
            }

        sources[source_key]["chunk_numbers"].append(f"[{index}]")

    for source in sources.values():
        chunk_numbers = ", ".join(source["chunk_numbers"])
        title = source["title"]
        source_url = source["source_url"]

        if source_url:
            lines.append(f"- {title} ({chunk_numbers}): {source_url}")
        else:
            lines.append(f"- {title} ({chunk_numbers})")

    return "\n".join(lines)


def generate_answer(
    question: str,
    api_key: str,
    history: ChatHistory | None = None,
) -> tuple[str, list]:
    """Generate a non-streaming answer and return the retrieved nodes."""

    settings = load_settings()
    history = history or []

    if not api_key.strip():
        raise ValueError("Please paste your OpenAI API key before asking a question.")

    if not question.strip():
        raise ValueError("Ask a chess strategy question to get started.")

    retrieved_nodes = retrieve_nodes(question, api_key, history)
    user_prompt = build_user_prompt(question, retrieved_nodes, history)

    llm = OpenAI(
        model=settings.llm_model,
        api_key=api_key,
        temperature=settings.llm_temperature,
    )
    response = llm.chat(build_messages(user_prompt))
    answer = str(response.message.content)

    return answer, retrieved_nodes


def stream_answer(
    question: str,
    api_key: str,
    history: ChatHistory | None = None,
) -> Generator[str]:
    """Stream an answer to a chess question using the RAG pipeline."""

    settings = load_settings()
    history = history or []

    if not api_key.strip():
        yield "Please paste your OpenAI API key before asking a question."
        return

    if not question.strip():
        yield "Ask a chess strategy question to get started."
        return

    retrieved_nodes = retrieve_nodes(question, api_key, history)
    user_prompt = build_user_prompt(question, retrieved_nodes, history)

    llm = OpenAI(
        model=settings.llm_model,
        api_key=api_key,
        temperature=settings.llm_temperature,
    )

    messages = build_messages(user_prompt)

    answer = ""
    for response in llm.stream_chat(messages):
        if response.delta:
            answer += response.delta
            yield answer

    yield answer + format_sources(retrieved_nodes)
