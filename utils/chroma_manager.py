"""
ChromaDB manager for shared vector memory.
Includes error handling and recovery for corrupted databases.
"""

import uuid
import logging
import shutil
from pathlib import Path
from datetime import datetime

import chromadb

from app.embeddings.local_embeddings import (
    get_embedding_model
)

from utils.config import Config

logger = logging.getLogger(__name__)


class ChromaManager:

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ):

        self.embedding_model = (
            get_embedding_model()
        )

        persist = persist_directory or Config.CHROMA_PERSIST_DIR
        coll_name = collection_name or Config.CHROMA_COLLECTION_NAME

        try:
            self.client = chromadb.PersistentClient(
                path=persist
            )

            self.collection = (
                self.client.get_or_create_collection(
                    name=coll_name
                )
            )

            logger.info(
                "ChromaDB initialized successfully"
            )
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            logger.warning("Attempting to recover by clearing corrupted database...")
            
            # Backup and reset the corrupted database
            if Path(persist).exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{persist}.backup.{timestamp}"
                try:
                    shutil.move(persist, backup_path)
                    logger.info(f"Corrupted database backed up to: {backup_path}")
                except Exception as backup_err:
                    logger.warning(f"Could not backup database: {backup_err}")
            
            # Try again with fresh database
            try:
                Path(persist).mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=persist
                )
                self.collection = (
                    self.client.get_or_create_collection(
                        name=coll_name
                    )
                )
                logger.info("ChromaDB recovered and reinitialized successfully")
            except Exception as recovery_err:
                logger.error(f"Failed to recover ChromaDB: {recovery_err}")
                raise RuntimeError(f"Cannot initialize ChromaDB: {recovery_err}")

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict] | None = None
    ):

        if not documents:
            return

        try:
            embeddings = (
                self.embedding_model.embed_batch(
                    documents
                )
            )

            ids = [
                str(uuid.uuid4())
                for _ in documents
            ]

            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(
                f"Added {len(documents)} documents"
            )
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise RuntimeError(f"Failed to store documents in ChromaDB: {e}")

    def document_exists(self, doc_id: str) -> bool:
        results = self.collection.get(
            where={"doc_id": doc_id},
            limit=1
        )
        return len(results.get("ids", [])) > 0

    def store_chunks(self, chunks: list[dict], file_name: str, doc_id: str) -> int:
        """Store document chunks with error handling."""
        try:
            documents = []
            metadatas = []
            for chunk in chunks:
                documents.append(chunk["text"])
                metadatas.append({
                    "file_name": file_name,
                    "doc_id": doc_id,
                    "chunk_index": chunk.get("chunk_index", 0)
                })
            self.add_documents(documents=documents, metadatas=metadatas)
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise RuntimeError(f"Failed to store document chunks: {e}")

    def get_full_text(self, doc_id: str) -> str:
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        chunks = list(zip(documents, metadatas))
        chunks.sort(key=lambda x: x[1].get("chunk_index", 0))
        
        return "\n\n".join(doc for doc, meta in chunks)

    def get_collection_stats(self) -> dict:
        return {
            "count": self.collection.count()
        }

    def list_documents(self, max_chunks: int = 5000) -> list[dict]:
        """
        Return unique documents present in the collection (deduped by doc_id).
        Scans chunk metadatas up to max_chunks for responsiveness.
        """
        results = self.collection.get(
            include=["metadatas"],
            limit=max_chunks,
        )
        metadatas = results.get("metadatas") or []
        by_doc: dict[str, dict] = {}
        for meta in metadatas:
            if not meta:
                continue
            did = meta.get("doc_id")
            if not did:
                continue
            if did not in by_doc:
                fname = meta.get("file_name") or "unknown"
                by_doc[did] = {
                    "id": did,
                    "doc_id": did,
                    "name": fname,
                    "file_name": fname,
                }
        return list(by_doc.values())

    # ─────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_id: str = None
    ):

        query_embedding = (
            self.embedding_model.embed(
                query
            )
        )

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }
        if doc_id:
            kwargs["where"] = {"doc_id": doc_id}

        results = self.collection.query(**kwargs)

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        formatted_results = []

        for doc, meta, dist in zip(
            documents,
            metadatas,
            distances
        ):

            formatted_results.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "distance": dist
                }
            )

        logger.info(
            f"Retrieved {len(formatted_results)} chunks"
        )

        return formatted_results


# ─────────────────────────────────────
# Singleton Access
# ─────────────────────────────────────

_chroma_manager_instance = None


def get_chroma_manager():

    global _chroma_manager_instance

    if _chroma_manager_instance is None:

        _chroma_manager_instance = (
            ChromaManager()
        )

    return _chroma_manager_instance


def reset_chroma_database():
    """
    Reset the ChromaDB database safely.
    Backs up existing data and creates a fresh database.
    """
    global _chroma_manager_instance
    
    persist_dir = Config.CHROMA_PERSIST_DIR
    
    # Invalidate the cached instance
    _chroma_manager_instance = None
    
    if Path(persist_dir).exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{persist_dir}.backup.{timestamp}"
        try:
            shutil.move(persist_dir, backup_path)
            logger.info(f"ChromaDB backed up to: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            # Still try to proceed
    
    # Create fresh database
    try:
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        logger.info("ChromaDB database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False