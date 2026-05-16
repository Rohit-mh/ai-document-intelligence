"""
Summarizer Agent.

Generates document summaries using the abstracted LLM provider.
"""

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from typing import AsyncGenerator, Any
from pydantic import PrivateAttr

from app.llm.provider_factory import get_llm_provider


class SummarizerAgent(BaseAgent):
    """Generates concise or detailed summaries from text context."""
    
    _llm: Any = PrivateAttr(default=None)

    def __init__(self, name="summarizer_agent", **kwargs):
        super().__init__(name=name, **kwargs)

    def _llm_client(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        full_text = ctx.session.state.get("current_doc_text", "")
        summary_type = ctx.session.state.get("summary_type", "concise")
        
        if not full_text:
            yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text="No document text available to summarize.")]))
            return
            
        length_instruction = "under 300 words" if summary_type == "concise" else "between 500 and 1000 words"
        
        messages = [
            {"role": "system", "content": f"You are a professional summarizer. Summarize the text precisely and keep it {length_instruction}."},
            {"role": "user", "content": f"Document text:\n{full_text[:15000]}"} # Truncated to avoid context limits
        ]
        
        response = self._llm_client().generate(messages)
        
        ctx.session.state[f"{summary_type}_summary"] = response
        
        yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text=response)]))

summarizer_agent = SummarizerAgent()