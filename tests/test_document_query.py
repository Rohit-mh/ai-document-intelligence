"""
Test document query functionality with ChromaDB and LLM.
"""

import pytest

@pytest.mark.asyncio
async def test_document_query_pipeline():
    """Test full document query pipeline using ChromaDB and LLM."""
    from utils.chroma_manager import get_chroma_manager
    from app.llm.provider_factory import get_llm_provider
    
    db = get_chroma_manager()
    llm = get_llm_provider()
    
    query = "What are the key points discussed in the document?"
    
    # Search ChromaDB
    results = db.search(query=query, top_k=3)
    
    # Build context from results
    context = "\n\n".join(result["text"] for result in results)
    
    # Generate answer using LLM
    messages = [
        {
            "role": "system",
            "content": (
                "Answer ONLY using provided context. "
                "If information is missing, say "
                "'Information not found in document.'"
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{query}"
        }
    ]
    
    response = llm.generate(messages)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0