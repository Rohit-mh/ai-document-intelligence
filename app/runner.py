"""
ADK Runner Script — Programmatic execution of the Document Intelligence System.

Following adk-skill.skills.md Section 10 (Runner & Execution):
- Runner orchestrates agent execution
- InMemorySessionService for development
- run_async event loop for processing
- Helper pattern for agent interaction

This script provides a programmatic API that the FastAPI backend
and Streamlit UI use to interact with the ADK agents.
"""

import hashlib
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from utils.config import Config
from utils.chroma_manager import get_chroma_manager
from utils.llm_client import call_llm, call_llm_json, truncate_for_groq
from utils.document_processor import process_document

logger = logging.getLogger(__name__)

APP_NAME = "document_intelligence"
USER_ID = "default_user"
SESSION_ID = "default_session"


def _chroma_persist_size_mb(persist_dir: str) -> float:
    """Approximate on-disk size of the Chroma persist directory (MB)."""
    root = Path(persist_dir)
    if not root.is_dir():
        return 0.0
    total = 0
    try:
        for p in root.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except OSError:
        return 0.0
    return round(total / (1024 * 1024), 2)


class DocumentIntelligenceRunner:
    """
    Programmatic interface to the Document Intelligence multi-agent system.
    
    Uses ADK Runner for agent orchestration and provides direct tool-call
    methods for the Streamlit UI and FastAPI backend.
    
    Following adk-skill.skills.md Section 10 patterns.
    """

    def __init__(self):
        Config.ensure_directories()
        self.chroma = get_chroma_manager()
        self._current_doc_id = None
        self._current_file_name = None
        logger.info("DocumentIntelligenceRunner initialized.")

    @property
    def current_doc_id(self):
        return self._current_doc_id

    @property
    def current_file_name(self):
        return self._current_file_name

    # ──────────────────────────────────────────────
    # Document Processing (Extractor Agent logic)
    # ──────────────────────────────────────────────

    def process_document(self, file_path: str) -> dict:
        """
        Process a document: extract → clean → chunk → embed → store.
        Calls the Extractor Agent's tool logic directly.
        """
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        doc_id = hashlib.md5(f"{file_name}_{file_size}".encode()).hexdigest()[:12]

        # Check if already processed
        if self.chroma.document_exists(doc_id):
            self._current_doc_id = doc_id
            self._current_file_name = file_name
            return {
                "status": "already_processed",
                "doc_id": doc_id,
                "file_name": file_name,
                "message": f"'{file_name}' is already processed and ready.",
            }

        # Full pipeline: extract → clean → chunk
        doc_data = process_document(file_path)

        # Store chunks with embeddings
        chunks_stored = self.chroma.store_chunks(
            chunks=doc_data["chunks"],
            file_name=file_name,
            doc_id=doc_id,
        )

        self._current_doc_id = doc_id
        self._current_file_name = file_name

        return {
            "status": "success",
            "doc_id": doc_id,
            "file_name": file_name,
            "total_characters": doc_data["total_characters"],
            "total_chunks": chunks_stored,
            "message": f"Processed '{file_name}': {doc_data['total_characters']} chars, {chunks_stored} chunks.",
        }

    def save_and_process(self, file_name: str, file_bytes: bytes) -> dict:
        """Save uploaded file and process it."""
        Config.ensure_directories()
        save_path = os.path.join(Config.UPLOAD_DIR, file_name)
        with open(save_path, "wb") as f:
            f.write(file_bytes)
        return self.process_document(save_path)

    # ──────────────────────────────────────────────
    # Summarization (Summarizer Agent logic)
    # ──────────────────────────────────────────────

    def get_concise_summary(self, doc_id: str = None) -> dict:
        """Generate concise summary using Azure OpenAI GPT-5.1."""
        doc_id = doc_id or self._current_doc_id
        if not doc_id:
            return {"status": "error", "message": "No document loaded."}

        full_text = self.chroma.get_full_text(doc_id)
        if not full_text.strip():
            return {"status": "error", "message": "No text found for this document."}

        if len(full_text) > 24000:
            full_text = full_text[:24000] + "\n\n[... document truncated for free tier limits ...]"

        system_prompt = """You are an expert document summarizer. Generate a CONCISE summary.
Rules:
- Under 300 words
- Capture main purpose, key findings, conclusions
- Use bullet points for key points
- Start with a one-sentence overview"""

        summary = call_llm(
            f"Summarize concisely:\n\n{full_text}",
            system_prompt, temperature=0.1, max_tokens=1000,
        )
        return {"status": "success", "doc_id": doc_id, "summary_type": "concise", "summary": summary}

    def get_detailed_summary(self, doc_id: str = None) -> dict:
        """Generate detailed summary using Azure OpenAI GPT-5.1."""
        doc_id = doc_id or self._current_doc_id
        if not doc_id:
            return {"status": "error", "message": "No document loaded."}

        full_text = self.chroma.get_full_text(doc_id)
        if not full_text.strip():
            return {"status": "error", "message": "No text found for this document."}

        if len(full_text) > 24000:
            full_text = full_text[:24000] + "\n\n[... document truncated for free tier limits ...]"

        system_prompt = """You are an expert document analyst. Generate a DETAILED summary.
Rules:
- Cover all major sections and topics thoroughly
- Include key data points and statistics
- Organize by sections with headers
- Target 500-1000 words"""

        summary = call_llm(
            f"Provide a detailed summary:\n\n{full_text}",
            system_prompt, temperature=0.1, max_tokens=3000,
        )
        return {"status": "success", "doc_id": doc_id, "summary_type": "detailed", "summary": summary}

    # ──────────────────────────────────────────────
    # Q&A (Q&A Agent logic)
    # ──────────────────────────────────────────────

    def answer_question(self, question: str, doc_id: str = None) -> dict:
        """Answer a question using RAG with Azure OpenAI GPT-5.1."""
        doc_id = doc_id or self._current_doc_id
        if not doc_id:
            # Fallback to general chat if no document is uploaded
            answer = call_llm(
                user_prompt=question,
                system_prompt="You are a helpful AI assistant. Answer the user's questions clearly and concisely.",
                temperature=0.7, 
                max_tokens=2000
            )
            return {"status": "success", "answer": answer, "sources": [], "question": question}

        # Retrieve relevant chunks
        results = self.chroma.search(query=question, top_k=Config.TOP_K_RESULTS, doc_id=doc_id)
        if not results:
            return {
                "status": "no_context",
                "answer": "No relevant information found in the document.",
                "sources": [],
            }

        # Build context
        context_parts = []
        sources = []
        for i, r in enumerate(results):
            idx = r["metadata"].get("chunk_index", "?")
            context_parts.append(f"{r['text']}")
            sources.append({
                "chunk_index": idx,
                "file_name": r["metadata"].get("file_name", "unknown"),
                "similarity": round(1 - r["distance"], 4),
                "preview": r["text"][:150] + "...",
            })

        context = "\n\n---\n\n".join(context_parts)

        system_prompt = """You are a document Q&A assistant. Answer ONLY from the provided context. Keep your response natural and do not mention source numbers or chunks.
RULES:
1. Answer ONLY using the provided context
2. If context doesn't have enough info, say so
3. Never make up information"""

        answer = call_llm(
            f"Context:\n{context}\n\n---\nQuestion: {question}\n\nAnswer from context only:",
            system_prompt, temperature=0.1, max_tokens=2000,
        )
        return {"status": "success", "answer": answer, "sources": sources, "question": question}

    # ──────────────────────────────────────────────
    # Insights (Insights Agent logic)
    # ──────────────────────────────────────────────

    def get_insights(self, doc_id: str = None) -> dict:
        """Extract insights using Azure OpenAI GPT-5.1."""
        doc_id = doc_id or self._current_doc_id
        if not doc_id:
            return {"status": "error", "message": "No document loaded."}

        full_text = self.chroma.get_full_text(doc_id)
        if not full_text.strip():
            return {"status": "error", "message": "No text found for this document."}

        if len(full_text) > 24000:
            full_text = full_text[:24000] + "\n\n[... document truncated for free tier limits ...]"

        system_prompt = """Analyze the document and return a JSON object:
{
  "themes": ["3-7 major themes"],
  "key_insights": ["5-10 key insights"],
  "action_items": ["actionable recommendations"],
  "important_points": ["critical facts and conclusions"]
}
Return ONLY valid JSON."""

        try:
            result = call_llm_json(f"Analyze:\n\n{full_text}", system_prompt)
            return {
                "status": "success",
                "doc_id": doc_id,
                "themes": result.get("themes", []),
                "key_insights": result.get("key_insights", []),
                "action_items": result.get("action_items", []),
                "important_points": result.get("important_points", []),
            }
        except Exception:
            # Fallback
            raw = call_llm(f"Analyze:\n\n{full_text}", system_prompt.replace("Return ONLY valid JSON.", ""), temperature=0.1)
            return {"status": "success", "doc_id": doc_id, "raw_insights": raw}

    # ──────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get current system stats."""
        chroma_stats = self.chroma.get_collection_stats()
        documents = self.chroma.list_documents()
        chunk_count = chroma_stats.get("count", 0)
        persist_mb = _chroma_persist_size_mb(Config.CHROMA_PERSIST_DIR)
        return {
            "current_doc_id": self._current_doc_id,
            "current_file_name": self._current_file_name,
            "chroma_stats": chroma_stats,
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": chunk_count,
            "total_embeddings": chunk_count,
            "database_size_mb": persist_mb,
            "config": Config.get_summary(),
        }


# Singleton instance
_runner_instance: DocumentIntelligenceRunner | None = None

def get_runner() -> DocumentIntelligenceRunner:
    global _runner_instance
    if _runner_instance is None:
        _runner_instance = DocumentIntelligenceRunner()
    return _runner_instance
