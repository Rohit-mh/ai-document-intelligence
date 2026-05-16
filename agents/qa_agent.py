"""
Q&A Agent.

Implements Retrieval-Augmented Generation (RAG)
using Groq API and ChromaDB.
"""

import logging

from typing import AsyncGenerator, Any
from pydantic import PrivateAttr

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from app.llm.provider_factory import get_llm_provider
from utils.chroma_manager import get_chroma_manager


logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """RAG-based question answering agent."""

    _llm: Any = PrivateAttr(default=None)
    _chroma: Any = PrivateAttr(default=None)

    def __init__(self, name="qa_agent", **kwargs):

        super().__init__(
            name=name,
            description="Answers questions using RAG",
            **kwargs
        )

    def _llm_client(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    def _chroma_mgr(self):
        if self._chroma is None:
            self._chroma = get_chroma_manager()
        return self._chroma

    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:

        query = ctx.session.state.get("user_query")

        if not query:

            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text="No query provided."
                        )
                    ]
                )
            )

            return

        try:

            top_k = int(
                ctx.session.state.get("top_k", 5)
            )

            doc_id = ctx.session.state.get("current_doc_id")

            retrieved_chunks = self._chroma_mgr().search(
                query,
                top_k=top_k,
                doc_id=doc_id,
            )

            if not retrieved_chunks:

                yield Event(
                    author=self.name,
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part(
                                text="No relevant context found."
                            )
                        ]
                    )
                )

                return

            logger.info(
                f"Retrieved {len(retrieved_chunks)} chunks"
            )

            context_text = "\n\n".join(
    chunk["text"]
    for chunk in retrieved_chunks
)

            system_prompt = """
You are a document intelligence assistant.

Rules:
- Answer ONLY using provided context
- If information is missing, say:
  'Information not found in document.'
- Never hallucinate
"""

            user_prompt = f"""
Context:
{context_text}

Question:
{query}
"""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]

            response = self._llm_client().generate(
                messages
            )

        except Exception as e:

            logger.exception(
                "QA agent execution failed"
            )

            response = (
                "An error occurred while processing the query."
            )

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(text=response)
                ]
            )
        )

qa_agent = QAAgent()