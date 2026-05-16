"""
Test vector pipeline functionality with ChromaDB.
"""

import pytest


def test_vector_pipeline_add_and_search():
    """Test adding documents to ChromaDB and searching them."""
    from utils.chroma_manager import get_chroma_manager
    
    db = get_chroma_manager()
    
    sample_chunks = [
        "Artificial Intelligence is transforming industries.",
        "Multi-agent systems coordinate multiple AI agents.",
        "ChromaDB is a vector database for embeddings.",
    ]
    
    metadata = [
        {"source": "doc1"},
        {"source": "doc1"},
        {"source": "doc1"},
    ]
    
    # Add documents
    db.add_documents(documents=sample_chunks, metadatas=metadata)
    
    # Search for documents
    results = db.search("What is a vector database?", top_k=2)
    
    assert results is not None
    assert isinstance(results, list)
    assert len(results) > 0