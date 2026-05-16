"""
Main entry point for the Document Intelligence System.

Usage:
    # Run Streamlit UI:
    streamlit run app/streamlit_app.py

    # Run FastAPI backend:
    uvicorn app.api:app --reload --port 8000

    # Run ADK Dev UI:
    adk web .

    # Run ADK CLI:
    adk run .

    # Run this script for quick test:
    python app.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

from utils.config import Config


def main():
    """Validate config and show system status."""
    print("=" * 60)
    print("  Document Intelligence System")
    print("  Multi-Agent AI • Azure OpenAI • Google ADK • ChromaDB")
    print("=" * 60)
    print()

    # Validate configuration
    missing = Config.validate()
    if missing:
        print(f"⚠️  Missing environment variables: {', '.join(missing)}")
        print("   Copy .env.example to .env and fill in your credentials.")
        print()
    else:
        print("✅ Configuration valid.")
        print()

    # Show config summary
    summary = Config.get_summary()
    print("Configuration:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print()

    print("Available commands:")
    print("  streamlit run app/streamlit_app.py    — Launch UI")
    print("  uvicorn app.api:app --reload          — Launch API")
    print("  adk web .                             — ADK Dev UI")
    print("  adk run .                             — ADK CLI")
    print()


if __name__ == "__main__":
    main()
