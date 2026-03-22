import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


def get_query_engine(topic_filter=None, bank_filter=None):
    embed_model = HuggingFaceEmbedding(
        model_name="Metric-AI/armenian-text-embeddings-2-large",
        device="cpu"
    )

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("bank_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
        storage_context=storage_context,
    )

    # metadata filters if needed
    filters = {}
    if topic_filter:
        filters["topic"] = topic_filter
    if bank_filter:
        filters["bank"] = bank_filter

    query_engine = index.as_query_engine(
        similarity_top_k=10,
        filters=filters if filters else None,
    )

    return query_engine