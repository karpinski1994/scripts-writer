#!/usr/bin/env python3
"""Ingestion script for global hook FAISS index.

Run this script to load hook documents from backend/documents/hook/ into a global FAISS index.
Run manually whenever hook templates are updated.

Usage:
    python backend/scripts/ingest_hook_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.faiss_service import create_global_index, global_index_exists


DOCS_PATH = "/Users/karpinski94/projects/scripts-writer/backend/documents/hook"
INDEX_NAME = "global_hooks"


def main():
    print(f"=== Global Hook FAISS Ingestion ===")
    print(f"Source: {DOCS_PATH}")
    print(f"Index: {INDEX_NAME}")

    if global_index_exists(INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Rebuilding...")

    print(f"Loading documents from {DOCS_PATH}...")
    create_global_index(DOCS_PATH, INDEX_NAME)
    print(f"Global hook index created successfully!")
    print(f"Index location: data/faiss_indexes/{INDEX_NAME}/")


if __name__ == "__main__":
    main()
