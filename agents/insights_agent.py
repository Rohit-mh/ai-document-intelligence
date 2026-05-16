"""
Insights Agent.

Extracts themes and action items using JSON structured output via Groq API.
"""

import json
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from typing import AsyncGenerator, Any
from pydantic import PrivateAttr

from app.llm.provider_factory import get_llm_provider


class InsightsAgent(BaseAgent):
    """Extracts structured insights from document text."""
    
    _llm: Any = PrivateAttr(default=None)

    def __init__(self, name="insights_agent", **kwargs):
        super().__init__(name=name, **kwargs)

    def _llm_client(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        full_text = ctx.session.state.get("current_doc_text", "")
        
        if not full_text:
            yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text="No document text available.")]))
            return
            
        messages = [
            {"role": "system", "content": "Extract document insights. Create keys: 'themes' (list), 'key_insights' (list), 'action_items' (list)."},
            {"role": "user", "content": f"Extract insights from this text:\n{full_text[:15000]}"}
        ]
        
        # Utilize structured output capabilities of the provider abstraction
        response_dict = self._llm_client().generate_json(messages)
        
        ctx.session.state["document_insights"] = response_dict
        
        yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text=json.dumps(response_dict, indent=2))]))

insights_agent = InsightsAgent()