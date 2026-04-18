import os
import pickle
import shutil
from pathlib import Path
from typing import Any

import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

FAISS_INDEX_BASE = Path("data/faiss_indexes")
ICP_QUERY = (
    "form an icp (ideal customer profile) from all the documents take most common lead awarness levels, "
    "identities, pain points, goals, dreams, desires, internal conficts, doubts, enemies, external barriers, "
    "failed attempts, what did not work, the emotional drivers - why now, and what makes them buy and "
    "give me detailed report with quotes based on that"
)


def _get_project_index_dir(project_id: str) -> Path:
    return FAISS_INDEX_BASE / project_id


def _get_global_index_dir(index_name: str) -> Path:
    return FAISS_INDEX_BASE / index_name


def load_documents(docs_path: str) -> list[dict[str, Any]]:
    """Load all .txt files from the docs directory."""
    docs_path = Path(docs_path)
    if not docs_path.exists():
        raise FileNotFoundError(f"The directory {docs_path} does not exist.")

    documents = []
    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            filepath = docs_path / filename
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({"text": content, "source": filename})

    if not documents:
        raise FileNotFoundError(f"No .txt files found in {docs_path}.")

    return documents


def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - chunk_overlap
    return chunks


def create_index(documents: list[dict[str, Any]], project_id: str) -> None:
    """Create FAISS index with TF-IDF embeddings for a project."""
    project_dir = _get_project_index_dir(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    all_metadatas = []

    for doc in documents:
        chunks = split_text(doc["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": doc["source"]})

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))

    embeddings = vectorizer.fit_transform(all_chunks).toarray().astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(project_dir / "index.faiss"))

    with open(project_dir / "metadata.pkl", "wb") as f:
        pickle.dump(
            {"texts": all_chunks, "metadatas": all_metadatas, "vectorizer": vectorizer},
            f,
        )


def load_index(project_id: str) -> tuple[faiss.Index, list[str], list[dict[str, Any]], TfidfVectorizer]:
    """Load FAISS index from disk for a project."""
    project_dir = _get_project_index_dir(project_id)

    if not (project_dir / "index.faiss").exists():
        raise FileNotFoundError(f"No index found for project {project_id}")

    index = faiss.read_index(str(project_dir / "index.faiss"))

    with open(project_dir / "metadata.pkl", "rb") as f:
        data = pickle.load(f)

    return index, data["texts"], data["metadatas"], data["vectorizer"]


def search_project_documents(project_id: str, query: str, k: int = 5) -> list[tuple[str, dict[str, Any], float]]:
    """Search indexed documents using FAISS, return top k chunks with metadata and distance."""
    index, texts, metas, vectorizer = load_index(project_id)

    query_embedding = vectorizer.transform([query]).toarray().astype("float32")
    distances, indices = index.search(query_embedding, k)

    results = []
    for j, i in enumerate(indices[0]):
        if i < len(texts):
            results.append((texts[i], metas[i], float(distances[0][j])))

    return results


def index_exists(project_id: str) -> bool:
    """Check if FAISS index exists for a project."""
    project_dir = _get_project_index_dir(project_id)
    return (project_dir / "index.faiss").exists()


def clear_index(project_id: str) -> None:
    """Delete FAISS index for a specific project."""
    project_dir = _get_project_index_dir(project_id)
    if project_dir.exists():
        shutil.rmtree(project_dir)


def clear_all_indexes() -> None:
    """Delete all FAISS indexes."""
    if FAISS_INDEX_BASE.exists():
        shutil.rmtree(FAISS_INDEX_BASE)


def list_indexed_projects() -> list[str]:
    """List all projects with existing FAISS indexes."""
    if not FAISS_INDEX_BASE.exists():
        return []

    projects = []
    for item in FAISS_INDEX_BASE.iterdir():
        if item.is_dir() and (item / "index.faiss").exists():
            projects.append(item.name)

    return sorted(projects)


def create_global_index(docs_path: str, index_name: str) -> None:
    """Create a global FAISS index (not project-specific)."""
    index_dir = _get_global_index_dir(index_name)
    index_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(docs_path)

    all_chunks = []
    all_metadatas = []

    for doc in documents:
        chunks = split_text(doc["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": doc["source"]})

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))

    embeddings = vectorizer.fit_transform(all_chunks).toarray().astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(index_dir / "index.faiss"))

    with open(index_dir / "metadata.pkl", "wb") as f:
        pickle.dump(
            {"texts": all_chunks, "metadatas": all_metadatas, "vectorizer": vectorizer},
            f,
        )


def load_global_index(index_name: str) -> tuple[faiss.Index, list[str], list[dict[str, Any]], TfidfVectorizer]:
    """Load a global FAISS index from disk."""
    index_dir = _get_global_index_dir(index_name)

    if not (index_dir / "index.faiss").exists():
        raise FileNotFoundError(f"No global index found: {index_name}")

    index = faiss.read_index(str(index_dir / "index.faiss"))

    with open(index_dir / "metadata.pkl", "rb") as f:
        data = pickle.load(f)

    return index, data["texts"], data["metadatas"], data["vectorizer"]


def search_global_documents(index_name: str, query: str, k: int = 5) -> list[tuple[str, dict[str, Any], float]]:
    """Search a global FAISS index, return top k chunks with metadata and distance."""
    index, texts, metas, vectorizer = load_global_index(index_name)

    query_embedding = vectorizer.transform([query]).toarray().astype("float32")
    distances, indices = index.search(query_embedding, k)

    results = []
    for j, i in enumerate(indices[0]):
        if i < len(texts):
            results.append((texts[i], metas[i], float(distances[0][j])))

    return results


def global_index_exists(index_name: str) -> bool:
    """Check if a global FAISS index exists."""
    index_dir = _get_global_index_dir(index_name)
    return (index_dir / "index.faiss").exists()
