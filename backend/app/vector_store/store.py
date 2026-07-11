"""ChromaDB vector store for RAG-based query agent."""
import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

logger = logging.getLogger(__name__)

_collection = None
_client = None


def get_chroma_client():
    """Lazy-init ChromaDB persistent client."""
    global _client
    if _client is None:
        _client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False,
        )) if hasattr(ChromaSettings, 'chroma_db_impl') else chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )
    return _client


def get_collection(name: str = "sebi_clauses"):
    """Get or create the clause embeddings collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=name,
            metadata={"description": "SEBI circular clause chunks for RAG"},
        )
    return _collection


def add_chunks_to_store(chunks: list[dict]):
    """Add clause chunks to the vector store for retrieval."""
    collection = get_collection()
    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        chunk_id = chunk.get("chunk_id", "")
        text = chunk.get("text", "")
        if not text.strip():
            continue
        ids.append(chunk_id)
        documents.append(text)
        metadatas.append({
            "chapter": chunk.get("chapter", ""),
            "section_id": chunk.get("section_id", ""),
            "page_number": str(chunk.get("page_number", "")),
            "circular_id": str(chunk.get("circular_id", "")),
        })

    if ids:
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )
        logger.info(f"Added {len(ids)} chunks to vector store")


def query_store(query_text: str, n_results: int = 5) -> list[dict]:
    """Query the vector store for relevant clause chunks."""
    collection = get_collection()
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        output = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0
                output.append({
                    "chunk_id": results["ids"][0][i] if results.get("ids") else "",
                    "text": doc,
                    "chapter": meta.get("chapter", ""),
                    "section_id": meta.get("section_id", ""),
                    "relevance_score": max(0, 1 - distance),  # Convert distance to similarity
                })
        return output
    except Exception as e:
        logger.error(f"Vector store query failed: {e}")
        return []
