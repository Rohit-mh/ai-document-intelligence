"""
Streamlit UI — Clean frontend for the Document Intelligence System.

Sections:
1. Upload Documents (PDF, DOCX, TXT)
2. Short Summary
3. Detailed Summary
4. Insights (themes, key insights, action items)
5. Chat with Document (Q&A)

Features:
- Loading indicators
- Clean layout
- Responsive interaction
- Document processing progress
- Error handling
"""

import streamlit as st
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from utils.config import Config
from app.runner import get_runner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Document Intelligence System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .insight-tag {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
    }
    
    .source-ref {
        background: rgba(72, 187, 120, 0.15);
        border-left: 3px solid #48bb78;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        margin: 4px 0;
        font-size: 0.85rem;
    }
    
    .status-success { color: #48bb78; }
    .status-error { color: #fc8181; }
    .status-info { color: #63b3ed; }
    
    div[data-testid="stSidebar"] {
        background: rgba(15, 15, 35, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Initialize Runner
# ──────────────────────────────────────────────

@st.cache_resource
def init_runner():
    return get_runner()


# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────

st.markdown('<h1 class="main-header">📄 Document Intelligence System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Agent AI • Azure OpenAI GPT-5.1 • Google ADK • ChromaDB</p>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ System Status")
    
    # Config validation
    missing = Config.validate()
    if missing:
        st.error(f"❌ Missing config: {', '.join(missing)}")
        st.info("Copy `.env.example` to `.env` and fill in your credentials.")
    else:
        st.success("✅ Configuration valid")
    
    st.markdown("---")
    
    # Current document info
    if st.session_state.doc_id:
        st.markdown("### 📋 Current Document")
        st.info(f"📄 **{st.session_state.file_name}**\n\n`doc_id: {st.session_state.doc_id}`")
    
    st.markdown("---")
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
    - **Extractor Agent** → Extract & chunk
    - **Summarizer Agent** → Summaries
    - **Q&A Agent** → RAG answers
    - **Insights Agent** → Themes & actions
    - **Orchestrator** → Coordination
    """)
    
    st.markdown("---")
    st.markdown("### 📦 Tech Stack")
    st.markdown("""
    - Google ADK (Agents)
    - Azure OpenAI GPT-5.1
    - ChromaDB (Vector Store)
    - FastAPI + Streamlit
    """)


# ──────────────────────────────────────────────
# Main Content — Tabs
# ──────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📤 Upload Document",
    "📝 Short Summary",
    "📖 Detailed Summary",
    "💡 Insights",
    "💬 Chat with Document",
])

runner = init_runner()

# ── Tab 1: Upload Documents ──
with tab1:
    st.markdown("### Upload Your Document")
    st.markdown("Supported formats: **PDF**, **DOCX**, **TXT** (supports 100+ pages)")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"],
        help="Upload a PDF, DOCX, or TXT file to analyze",
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        with col2:
            process_btn = st.button("🚀 Process Document", type="primary", use_container_width=True)
        
        if process_btn:
            with st.spinner("🔄 Processing document... (extract → clean → chunk → embed → store)"):
                try:
                    result = runner.save_and_process(uploaded_file.name, uploaded_file.read())
                    
                    if result["status"] == "success":
                        st.session_state.doc_id = result["doc_id"]
                        st.session_state.file_name = result["file_name"]
                        st.session_state.processing_done = True
                        st.session_state.chat_history = []
                        
                        st.success(f"✅ {result['message']}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Characters", f"{result['total_characters']:,}")
                        with col_b:
                            st.metric("Chunks", result['total_chunks'])
                        with col_c:
                            st.metric("Doc ID", result['doc_id'])
                    
                    elif result["status"] == "already_processed":
                        st.session_state.doc_id = result["doc_id"]
                        st.session_state.file_name = result["file_name"]
                        st.session_state.processing_done = True
                        st.info(f"ℹ️ {result['message']}")
                    
                    else:
                        st.error(f"❌ {result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")


# ── Tab 2: Short Summary ──
with tab2:
    st.markdown("### 📝 Concise Summary")
    
    if not st.session_state.doc_id:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.info(f"Document: **{st.session_state.file_name}**")
        
        if st.button("Generate Short Summary", type="primary", key="btn_short"):
            with st.spinner("🤖 Generating concise summary via Azure OpenAI GPT-5.1..."):
                try:
                    result = runner.get_concise_summary(st.session_state.doc_id)
                    if result["status"] == "success":
                        st.markdown("---")
                        st.markdown(result["summary"])
                    else:
                        st.error(f"❌ {result.get('message', 'Summary generation failed.')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ── Tab 3: Detailed Summary ──
with tab3:
    st.markdown("### 📖 Detailed Summary")
    
    if not st.session_state.doc_id:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.info(f"Document: **{st.session_state.file_name}**")
        
        if st.button("Generate Detailed Summary", type="primary", key="btn_detailed"):
            with st.spinner("🤖 Generating detailed summary via Azure OpenAI GPT-5.1..."):
                try:
                    result = runner.get_detailed_summary(st.session_state.doc_id)
                    if result["status"] == "success":
                        st.markdown("---")
                        st.markdown(result["summary"])
                    else:
                        st.error(f"❌ {result.get('message', 'Summary generation failed.')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ── Tab 4: Insights ──
with tab4:
    st.markdown("### 💡 Document Insights")
    
    if not st.session_state.doc_id:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.info(f"Document: **{st.session_state.file_name}**")
        
        if st.button("Extract Insights", type="primary", key="btn_insights"):
            with st.spinner("🤖 Extracting insights via Azure OpenAI GPT-5.1..."):
                try:
                    result = runner.get_insights(st.session_state.doc_id)
                    
                    if result["status"] == "success":
                        st.markdown("---")
                        
                        # Check if structured or raw
                        if "raw_insights" in result:
                            st.markdown(result["raw_insights"])
                        else:
                            # Themes
                            if result.get("themes"):
                                st.markdown("#### 🎯 Major Themes")
                                for theme in result["themes"]:
                                    st.markdown(f"- {theme}")
                            
                            # Key Insights
                            if result.get("key_insights"):
                                st.markdown("#### 🔍 Key Insights")
                                for insight in result["key_insights"]:
                                    st.markdown(f"- {insight}")
                            
                            # Action Items
                            if result.get("action_items"):
                                st.markdown("#### ✅ Action Items")
                                for item in result["action_items"]:
                                    st.markdown(f"- {item}")
                            
                            # Important Points
                            if result.get("important_points"):
                                st.markdown("#### ⚠️ Important Points")
                                for point in result["important_points"]:
                                    st.markdown(f"- {point}")
                    else:
                        st.error(f"❌ {result.get('message', 'Insights generation failed.')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ── Tab 5: Chat with Document ──
with tab5:
    st.markdown("### 💬 Chat with Your Document")
    
    if not st.session_state.doc_id:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.info(f"Document: **{st.session_state.file_name}** • Ask anything about this document!")
        
        # Chat history display
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📎 Sources"):
                        for src in msg["sources"]:
                            st.markdown(
                                f"**Chunk {src['chunk_index']}** "
                                f"(similarity: {src['similarity']}) — "
                                f"`{src['file_name']}`\n\n> {src['preview']}"
                            )
        
        # Chat input
        if question := st.chat_input("Ask a question about your document..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Generate answer
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching document & generating answer..."):
                    try:
                        result = runner.answer_question(question, st.session_state.doc_id)
                        
                        if result["status"] == "success":
                            st.markdown(result["answer"])
                            
                            # Show sources
                            if result.get("sources"):
                                with st.expander("📎 Sources"):
                                    for src in result["sources"]:
                                        st.markdown(
                                            f"**Chunk {src['chunk_index']}** "
                                            f"(similarity: {src['similarity']}) — "
                                            f"`{src['file_name']}`\n\n> {src['preview']}"
                                        )
                            
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": result["answer"],
                                "sources": result.get("sources", []),
                            })
                        else:
                            st.warning(result.get("answer", "Could not generate answer."))
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": result.get("answer", "No answer available."),
                            })
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
