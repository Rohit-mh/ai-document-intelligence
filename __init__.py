# Project root marker only.
# Do not import `agent` here: pytest imports this file and that eagerly loads
# torch/sentence-transformers and all ADK agents.
# ADK CLI: run from repo root so `agent.py` is found (`adk web .` / `adk run .`).
