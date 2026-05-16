"""
Orchestrator Agent.

Routes operations through the sequential pipeline or RAG retrieval based on user input.
Uses GitHub Models via LiteLLM so the ADK root agent matches Config / provider_factory.
"""

import os

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from agents.extractor_agent import ExtractorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.insights_agent import InsightsAgent
from agents.qa_agent import QAAgent


def _orchestrator_lite_llm() -> LiteLlm:
    """ADK orchestrator model: GitHub Models through LiteLLM (uses GITHUB_TOKEN from env)."""
    import os
    model = os.getenv("GITHUB_MODEL", "gpt-4o").strip() or "gpt-4o"
    base_url = "https://models.inference.ai.azure.com"
    api_key = os.getenv("GITHUB_TOKEN", "")
    # LiteLLM accepts openai-compatible endpoints via the openai/ prefix + api_base
    return LiteLlm(
        model=f"openai/{model}",
        api_base=base_url,
        api_key=api_key,
    )


# Sequential Ingestion and Processing Pipeline
ingestion_pipeline = SequentialAgent(
    name="ingestion_pipeline",
    sub_agents=[
        ExtractorAgent(name="extractor"),
        SummarizerAgent(name="summarizer"),
        InsightsAgent(name="insights"),
    ],
)

# RAG Query Pipeline
query_pipeline = QAAgent(name="qa_agent")

# Orchestrator (LiteLLM + GitHub Models — same credentials as provider_factory)
orchestrator_agent = LlmAgent(
    name="orchestrator",
    model=_orchestrator_lite_llm(),
    instruction=(
        "You are the document intelligence orchestrator.\n"
        "If the user is uploading a new document, route to 'ingestion_pipeline'.\n"
        "If the user is asking a question about a document, route to 'qa_agent'.\n"
        "Do not answer questions directly."
    ),
    description="Master orchestrator for document analysis and Q&A tasks.",
    sub_agents=[ingestion_pipeline, query_pipeline],
)
