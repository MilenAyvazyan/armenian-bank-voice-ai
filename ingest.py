import json
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

def ingest_data_llama():
    with open("data.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    documents = []
    for item in raw_data:
        doc = Document(
            text=item["text"],
            metadata={
                "bank": item["bank"],
                "topic": item["topic"]
            }
        )
        documents.append(doc)

    embed_model = HuggingFaceEmbedding(
        model_name="Metric-AI/armenian-text-embeddings-2-large",
        device="cpu"
    )

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("bank_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=50)],
        show_progress=True
    )

    print(f"done. ingested {len(documents)} documents into chroma")

if __name__ == "__main__":
    ingest_data_llama()