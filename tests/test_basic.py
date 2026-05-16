"""
Basic tests for the Document Intelligence System.
"""

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config_loads():
    """Test that configuration loads without errors."""
    from utils.config import Config
    assert Config.LLM_PROVIDER is not None
    assert Config.MAX_CHUNK_SIZE > 0
    assert Config.CHUNK_OVERLAP >= 0


def test_supported_extensions():
    """Test supported file extensions are defined."""
    from utils.config import Config
    assert ".pdf" in Config.SUPPORTED_EXTENSIONS
    assert ".docx" in Config.SUPPORTED_EXTENSIONS
    assert ".txt" in Config.SUPPORTED_EXTENSIONS


def test_document_processor_clean_text():
    """Test text cleaning function."""
    from utils.document_processor import clean_text
    
    raw = "  Hello   world  \n\n\n\n\nTest  "
    cleaned = clean_text(raw)
    assert "Hello world" in cleaned
    assert "\n\n\n" not in cleaned


def test_document_processor_chunk_text():
    """Test text chunking function."""
    from utils.document_processor import chunk_text
    
    text = "Hello world. " * 500  # Long text
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert all("text" in c for c in chunks)
    assert all("chunk_index" in c for c in chunks)


def test_config_ensure_directories():
    """Test directory creation."""
    from utils.config import Config
    Config.ensure_directories()
    assert os.path.exists(Config.UPLOAD_DIR)


def test_extract_text_from_txt(tmp_path):
    """Test TXT file extraction."""
    from utils.document_processor import extract_text_from_txt
    
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, this is a test document.", encoding="utf-8")
    
    result = extract_text_from_txt(str(test_file))
    assert "Hello" in result
    assert "test document" in result


def test_config_summary():
    """Test config summary generation."""
    from utils.config import Config
    summary = Config.get_summary()
    assert "llm_provider" in summary
    assert "chunk_size" in summary


def test_chroma_manager_singleton():
    """Test ChromaDB manager singleton pattern."""
    from utils.chroma_manager import get_chroma_manager
    
    manager1 = get_chroma_manager()
    manager2 = get_chroma_manager()
    
    assert manager1 is manager2, "ChromaManager should be a singleton"
    assert manager1.collection is not None


def test_document_processor_integration():
    """Test full document processing pipeline."""
    from utils.document_processor import process_document
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document. " * 100)
        temp_path = f.name
    
    try:
        result = process_document(temp_path)
        assert result.get("status") == "success" and "file_name" in result
        assert result["total_chunks"] > 0
        assert result["total_characters"] > 0
        assert len(result["chunks"]) == result["total_chunks"]
    finally:
        os.unlink(temp_path)


def test_text_extraction_supported_formats():
    """Test text extraction for supported formats."""
    from utils.document_processor import extract_text
    from pathlib import Path
    
    # Test TXT format
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content for extraction.")
        temp_txt = f.name
    
    try:
        extracted = extract_text(temp_txt)
        assert "Test content" in extracted
    finally:
        os.unlink(temp_txt)


@pytest.mark.asyncio
async def test_runner_initialization():
    """Test DocumentIntelligenceRunner initialization."""
    from app.runner import get_runner
    
    runner = get_runner()
    assert runner is not None
    assert runner.chroma is not None


def test_config_validation():
    """Test configuration validation."""
    from utils.config import Config
    
    # This may fail if credentials aren't set, but should at least return a list
    missing = Config.validate()
    assert isinstance(missing, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
