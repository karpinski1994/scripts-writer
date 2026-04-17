from six import print_
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from dotenv import load_dotenv

load_dotenv()


def load_documents(docs_path="docs"):
    """Load all text files from the docs directory"""
    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist.")

    documents = []
    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({"text": content, "source": filename})

    if not documents:
        raise FileNotFoundError(f"No .txt files found in {docs_path}.")

    for doc in documents[:2]:
        print(f"\nDocument: {doc['source']}, length: {len(doc['text'])}")

    return documents


def split_text(text, chunk_size=1000, chunk_overlap=200):
    """Split text into chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - chunk_overlap
    return chunks


def create_index(
    documents, persist_directory="db/faiss_index", chunk_size=1000, chunk_overlap=200
):
    """Create FAISS index with TF-IDF embeddings"""
    print("Creating TF-IDF embeddings...")

    all_chunks = []
    all_metadatas = []

    for doc in documents:
        chunks = split_text(doc["text"], chunk_size, chunk_overlap)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": doc["source"]})

    print(f"Total chunks: {len(all_chunks)}")

    vectorizer = TfidfVectorizer(
        max_features=5000, stop_words="english", ngram_range=(1, 2)
    )

    print("Fitting TF-IDF vectorizer...")
    embeddings = vectorizer.fit_transform(all_chunks).toarray().astype("float32")

    print(f"Embedding dimension: {embeddings.shape[1]}")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(persist_directory, exist_ok=True)
    faiss.write_index(index, os.path.join(persist_directory, "index.faiss"))

    with open(os.path.join(persist_directory, "metadata.pkl"), "wb") as f:
        pickle.dump(
            {"texts": all_chunks, "metadatas": all_metadatas, "vectorizer": vectorizer},
            f,
        )

    print(f"Index created with {index.ntotal} vectors")
    return index, all_chunks, all_metadatas, vectorizer


def load_index(persist_directory="db/faiss_index"):
    """Load FAISS index from disk"""
    index = faiss.read_index(os.path.join(persist_directory, "index.faiss"))

    with open(os.path.join(persist_directory, "metadata.pkl"), "rb") as f:
        data = pickle.load(f)

    return index, data["texts"], data["metadatas"], data["vectorizer"]


def search(query, k=5):
    """Search the index"""
    index, texts, metas, vectorizer = load_index()
    query_embedding = vectorizer.transform([query]).toarray().astype("float32")
    distances, indices = index.search(query_embedding, k)
    return [(texts[i], metas[i], distances[0][j]) for j, i in enumerate(indices[0])]


def main():
    """Main ingestion pipeline"""
    print("=== RAG Document Ingestion Pipeline ===\n")

    docs_path = "docs"
    persist_directory = "db/faiss_index"

    if os.path.exists(os.path.join(persist_directory, "index.faiss")):
        print("Vector store already exists.")
        index, texts, metas, _ = load_index(persist_directory)
        print(f"Loaded existing index with {index.ntotal} documents")
        return index, texts, metas

    print("Creating new vector store...\n")

    documents = load_documents(docs_path)
    index, texts, metas, vectorizer = create_index(documents, persist_directory)

    print("\nIngestion complete!")
    return index, texts, metas


def clear_db(persist_directory="db/faiss_index"):
    """Clear the vector database"""
    import shutil

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print("Database cleared.")
    else:
        print("No database found.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_db()
    else:
        main()
