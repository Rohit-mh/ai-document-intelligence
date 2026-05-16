"""
Document processing utilities for the Document Intelligence System.
Handles PDF, DOCX, and TXT file extraction, cleaning, and chunking.
Uses Pattern A (OCR/text extraction first) from the Azure OpenAI skill file.
"""

import os
import re
import logging
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.config import Config

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Document Text Extraction
# ──────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    Handles large documents (100+ pages) efficiently.
    
    Args:
        file_path: Path to the PDF file.
    
    Returns:
        Extracted text content.
    """
    try:
        doc = fitz.open(file_path)
        text_parts = []
        total_pages = len(doc)
        logger.info(f"Extracting text from PDF: {file_path} ({total_pages} pages)")

        for page_num in range(total_pages):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")

        doc.close()
        full_text = "\n\n".join(text_parts)
        logger.info(f"PDF extraction complete. Total characters: {len(full_text)}")
        return full_text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file using python-docx.
    Following the azure-openai-python skill file DOCX pattern.
    
    Args:
        file_path: Path to the DOCX file.
    
    Returns:
        Extracted text content.
    """
    try:
        doc = DocxDocument(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        logger.info(f"DOCX extraction complete. Total characters: {len(text)}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX {file_path}: {e}")
        raise


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.
    
    Args:
        file_path: Path to the TXT file.
    
    Returns:
        File content as text.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        logger.info(f"TXT extraction complete. Total characters: {len(text)}")
        return text
    except UnicodeDecodeError:
        # Fallback to latin-1 encoding
        with open(file_path, "r", encoding="latin-1") as f:
            text = f.read()
        logger.info(f"TXT extraction (latin-1 fallback) complete. Total characters: {len(text)}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from TXT {file_path}: {e}")
        raise


def extract_text(file_path: str) -> str:
    """
    Extract text from a document based on its file extension.
    
    Args:
        file_path: Path to the document.
    
    Returns:
        Extracted text content.
    
    Raises:
        ValueError: If the file type is not supported.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {Config.SUPPORTED_EXTENSIONS}")


# ──────────────────────────────────────────────
# Text Cleaning & Preprocessing
# ──────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean and preprocess extracted document text.
    
    Operations:
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove control characters
    - Strip leading/trailing whitespace
    
    Args:
        text: Raw extracted text.
    
    Returns:
        Cleaned text.
    """
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Normalize multiple newlines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize multiple spaces to single space
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Strip each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Remove leading/trailing whitespace
    text = text.strip()

    logger.info(f"Text cleaning complete. Final length: {len(text)} chars")
    return text


# ──────────────────────────────────────────────
# Text Chunking
# ──────────────────────────────────────────────

def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict]:
    """
    Split text into manageable chunks using LangChain's RecursiveCharacterTextSplitter.
    Supports large documents (100+ pages) efficiently.
    
    Args:
        text: The full document text.
        chunk_size: Maximum characters per chunk (default from config).
        chunk_overlap: Overlap between chunks (default from config).
    
    Returns:
        List of dicts with 'text', 'chunk_index', and 'char_start' keys.
    """
    chunk_size = chunk_size or Config.MAX_CHUNK_SIZE
    chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)

    chunks = []
    char_position = 0
    for i, chunk_text_content in enumerate(raw_chunks):
        start_pos = text.find(chunk_text_content, char_position)
        if start_pos == -1:
            start_pos = char_position

        chunks.append({
            "text": chunk_text_content,
            "chunk_index": i,
            "char_start": start_pos,
            "char_end": start_pos + len(chunk_text_content),
        })
        char_position = start_pos + len(chunk_text_content) - chunk_overlap

    logger.info(f"Chunking complete. Total chunks: {len(chunks)} (size={chunk_size}, overlap={chunk_overlap})")
    return chunks


# ──────────────────────────────────────────────
# Full Processing Pipeline
# ──────────────────────────────────────────────

def process_document(file_path: str) -> dict:
    """
    Full document processing pipeline: extract → clean → chunk.
    
    Args:
        file_path: Path to the document file.
    
    Returns:
        Dict with 'file_name', 'file_path', 'raw_text', 'clean_text',
        'chunks', 'total_chunks', 'total_characters'.
    """
    file_name = Path(file_path).name
    logger.info(f"Starting document processing: {file_name}")

    # Step 1: Extract text
    raw_text = extract_text(file_path)

    # Step 2: Clean text
    cleaned = clean_text(raw_text)

    # Step 3: Chunk text
    chunks = chunk_text(cleaned)

    result = {
        "status": "success",
        "file_name": file_name,
        "file_path": file_path,
        "raw_text": raw_text,
        "clean_text": cleaned,
        "chunks": chunks,
        "total_chunks": len(chunks),
        "total_characters": len(cleaned),
    }

    logger.info(
        f"Document processing complete: {file_name} | "
        f"{result['total_characters']} chars | {result['total_chunks']} chunks"
    )
    return result
