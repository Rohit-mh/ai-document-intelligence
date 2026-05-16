"""
Extractor Agent.

Handles:
- PDF/DOCX/TXT extraction
- text cleaning
- chunking
- embedding storage into ChromaDB
- ADK workflow integration
"""

import os
import logging

import fitz

from docx import Document

from pydantic import PrivateAttr

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import (
    InvocationContext,
)
from google.adk.events import Event
from google.genai import types

from typing import AsyncGenerator

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from utils.chroma_manager import ChromaManager, get_chroma_manager

logger = logging.getLogger(__name__)


class ExtractorAgent(BaseAgent):
    """
    Agent responsible for:
    - document ingestion
    - chunking
    - vector storage
    """

    # ─────────────────────────────────────
    # Private Attributes
    # ─────────────────────────────────────

    _chroma: ChromaManager | None = PrivateAttr(default=None)

    _text_splitter: RecursiveCharacterTextSplitter | None = PrivateAttr(default=None)

    # ─────────────────────────────────────
    # Initialization
    # ─────────────────────────────────────

    def __init__(
        self,
        name="extractor_agent",
        **kwargs
    ):

        super().__init__(
            name=name,
            **kwargs
        )

        self._text_splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=int(
                    kwargs.get(
                        "chunk_size",
                        1000
                    )
                ),
                chunk_overlap=int(
                    kwargs.get(
                        "chunk_overlap",
                        200
                    )
                ),
                length_function=len,
            )
        )

    def _chroma_mgr(self) -> ChromaManager:
        if self._chroma is None:
            self._chroma = get_chroma_manager()
        return self._chroma

    # ─────────────────────────────────────
    # Extract Text
    # ─────────────────────────────────────

    def extract_text(
        self,
        file_path: str
    ) -> str:

        logger.info(
            f"Extracting text from: {file_path}"
        )

        if file_path.endswith(".pdf"):

            text = ""

            doc = fitz.open(file_path)

            for page in doc:
                text += page.get_text()

            return text

        elif file_path.endswith(".docx"):

            doc = Document(file_path)

            return "\n".join(
                para.text
                for para in doc.paragraphs
            )

        elif file_path.endswith(".txt"):

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                return f.read()

        else:

            raise ValueError(
                f"Unsupported file type: {file_path}"
            )

    # ─────────────────────────────────────
    # Clean Text
    # ─────────────────────────────────────

    def clean_text(
        self,
        text: str
    ) -> str:

        text = text.replace(
            "\x00",
            " "
        )

        text = " ".join(
            text.split()
        )

        return text

    # ─────────────────────────────────────
    # Chunk Text
    # ─────────────────────────────────────

    def chunk_text(
        self,
        text: str
    ) -> list[str]:

        chunks = (
            self._text_splitter.split_text(
                text
            )
        )

        logger.info(
            f"Generated {len(chunks)} chunks"
        )

        return chunks

    # ─────────────────────────────────────
    # Main Processing Pipeline
    # ─────────────────────────────────────

    def process_document(
        self,
        file_path: str
    ):

        # Extract
        text = self.extract_text(
            file_path
        )

        logger.info(
            f"Extracted text length: {len(text)}"
        )

        # Clean
        cleaned_text = self.clean_text(
            text
        )

        # Chunk
        chunks = self.chunk_text(
            cleaned_text
        )

        # Metadata
        metadatas = [
            {
                "source": os.path.basename(
                    file_path
                )
            }
            for _ in chunks
        ]

        # Store in ChromaDB
        self._chroma_mgr().add_documents(
            documents=chunks,
            metadatas=metadatas
        )

        logger.info(
            f"Stored {len(chunks)} chunks in ChromaDB"
        )

        return {
            "status": "success",
            "source": file_path,
            "chunks_stored": len(chunks),
        }

    # ─────────────────────────────────────
    # ADK Async Workflow
    # ─────────────────────────────────────

    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:

        doc_id = ctx.session.state.get(
            "current_doc_id"
        )

        full_text = ctx.session.state.get(
            "current_doc_text"
        )

        if not doc_id or not full_text:

            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=(
                                "Error: Missing "
                                "document context."
                            )
                        )
                    ],
                ),
            )

            return

        logger.info(
            f"Processing document: {doc_id}"
        )

        # Clean
        cleaned_text = self.clean_text(
            full_text
        )

        # Chunk
        chunks = self.chunk_text(
            cleaned_text
        )

        # Store
        self._chroma_mgr().add_documents(
            documents=chunks,
            metadatas=[
                {
                    "source": doc_id
                }
                for _ in chunks
            ],
        )

        # Session State
        ctx.session.state[
            "extraction_status"
        ] = "success"

        ctx.session.state[
            "total_chunks"
        ] = len(chunks)

        response_text = (
            f"Successfully extracted "
            f"and embedded "
            f"{len(chunks)} chunks "
            f"for document {doc_id}."
        )

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=response_text
                    )
                ],
            ),
        )


# ─────────────────────────────────────
# Singleton Agent Instance
# ─────────────────────────────────────

extractor_agent = ExtractorAgent()


# ─────────────────────────────────────
# Helper Function
# ─────────────────────────────────────

def extract_and_store_document(
    file_path: str
):

    """
    Extract text from document,
    chunk it,
    and store embeddings in ChromaDB.
    """

    agent = ExtractorAgent()

    return agent.process_document(
        file_path=file_path
    )