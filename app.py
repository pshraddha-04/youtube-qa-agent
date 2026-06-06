# Phase 9: Streamlit Interface

import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage, AIMessage
from function_calling import build_agent, _state
import re

st.set_page_config(page_title="YouTube QA Agent", page_icon="▶️", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────
if "agent"        not in st.session_state:
    st.session_state.agent        = build_agent()
if "history"      not in st.session_state:
    st.session_state.history      = []
if "video_loaded" not in st.session_state:
    st.session_state.video_loaded = False
if "messages"     not in st.session_state:
    st.session_state.messages     = []
if "theme"        not in st.session_state:
    st.session_state.theme        = "dark"

# ── Markmap renderer with theme support ──────────────────────────────────────
def render_markmap(md: str, height: int = 500, dark: bool = True):
    bg      = "#0f1117" if dark else "#f0f2f6"
    colors  = "['#a78bfa','#6366f1','#34d399','#f472b6','#60a5fa']" if dark else "['#6366f1','#8b5cf6','#10b981','#f43f5e','#3b82f6']"
    text    = "#e2e8f0" if dark else "#1a202c"
    line    = "#2e3250" if dark else "#cbd5e1"
    html = f"""
    <style>
      .mm-wrap {{ background:{bg}; border-radius:12px; overflow:hidden; }}
      svg {{ width:100%; height:{height}px; background:{bg}; }}
      svg text, svg tspan {{ fill: {text} !important; }}
      .markmap-node-circle {{ stroke:{line}; }}
      .markmap-link {{ stroke:{line} !important; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.17"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-view@0.17"></script>
    <div class="mm-wrap"><svg id="mm"></svg></div>
    <script>
    (async () => {{
      const {{ Markmap, loadCSS, loadJS }} = window.markmap;
      const {{ Transformer }} = window.markmap;
      const transformer = new Transformer();
      const md = {repr(md)};
      const {{ root, features }} = transformer.transform(md);
      const {{ styles, scripts }} = transformer.getUsedAssets(features);
      if (styles) loadCSS(styles);
      if (scripts) await loadJS(scripts, {{ getMarkmap: () => window.markmap }});
      const svg = document.getElementById('mm');
      Markmap.create(svg, {{
        color: (node) => {colors}[node.depth % {colors}.length],
        duration: 400,
        maxWidth: 300,
        initialExpandLevel: 3,
      }}, root);
      svg.style.background = '{bg}';
      // Apply text color after render completes
      setTimeout(() => {{
        svg.querySelectorAll('text, tspan').forEach(t => {{
          t.style.fill = '{text}';
          t.style.color = '{text}';
        }});
      }}, 600);
    }})();
    </script>
    """
    components.html(html, height=height + 20)

# ── Theme colors ──────────────────────────────────────────────────────────────
is_dark = st.session_state.theme == "dark"

MAIN_BG        = "#0f1117" if is_dark else "#f0f2f6"
SIDEBAR_BG     = "#1a1c2e" if is_dark else "#e8eaf0"
SIDEBAR_BORDER = "#2e3250" if is_dark else "#c8ccd8"
SIDEBAR_TEXT   = "#a78bfa" if is_dark else "#4f46e5"
SIDEBAR_MUTED  = "#94a3b8" if is_dark else "#64748b"
SIDEBAR_BODY   = "#e2e8f0" if is_dark else "#1e293b"
SIDEBAR_INPUT  = "#1e2130" if is_dark else "#ffffff"
SIDEBAR_METRIC = "#1e2130" if is_dark else "#ffffff"
CHAT_BG        = "#1a1c2e" if is_dark else "#ffffff"
CHAT_BORDER    = "#2e3250" if is_dark else "#e2e8f0"
TEXT_PRIMARY   = "#e2e8f0" if is_dark else "#1a202c"
CARD_BG        = "#1a1c2e" if is_dark else "#ffffff"
CARD_BORDER    = "#2e3250" if is_dark else "#e2e8f0"
CARD_ICON_BG   = "#2e3250" if is_dark else "#ede9fe"
THEME_BTN_BG   = "#2e3250" if is_dark else "#ffffff"
THEME_BTN_TEXT = "#e2e8f0" if is_dark else "#1a202c"

st.markdown(f"""
<style>
/* Entire app background */
.stApp {{ background-color: {MAIN_BG}; }}

/* Remove default top padding from main block */
.block-container {{ padding-top: 0.5rem !important; }}

/* Sidebar theming */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {SIDEBAR_BORDER};
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: {SIDEBAR_TEXT} !important; }}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{ color: {SIDEBAR_BODY} !important; }}
[data-testid="stSidebar"] .stMarkdown p {{ color: {SIDEBAR_MUTED} !important; }}

/* Sidebar title size */
[data-testid="stSidebar"] h2 {{ font-size: 1.6rem !important; font-weight: 700 !important; }}

/* Sidebar section headers */
[data-testid="stSidebar"] h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; margin-top: 0.3rem !important; }}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
    min-height: 2.6rem !important;
    transition: all 0.3s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(99,102,241,0.4);
}}

/* Clear chat button */
.clear-btn button {{
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: white !important;
}}
.clear-btn button:hover {{
    box-shadow: 0 4px 15px rgba(239,68,68,0.4) !important;
}}

/* Sidebar text input */
[data-testid="stSidebar"] .stTextInput input {{
    background-color: {SIDEBAR_INPUT} !important;
    border: 1px solid {SIDEBAR_BORDER} !important;
    border-radius: 10px !important;
    color: {SIDEBAR_BODY} !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0.8rem !important;
    min-height: 2.4rem !important;
}}
[data-testid="stSidebar"] .stTextInput input:focus {{
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.3) !important;
}}
[data-testid="stSidebar"] .stTextInput input::placeholder {{
    color: {SIDEBAR_MUTED} !important;
    opacity: 1 !important;
}}

/* Sidebar metrics */
[data-testid="stSidebar"] [data-testid="stMetric"] {{
    background-color: {SIDEBAR_METRIC};
    border: 1px solid {SIDEBAR_BORDER};
    border-radius: 10px;
    padding: 0.9rem 0.8rem !important;
    box-shadow: {'none' if is_dark else '0 1px 4px rgba(0,0,0,0.08)'};
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{ color: {SIDEBAR_TEXT} !important; font-size: 1.4rem !important; }}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{ color: {SIDEBAR_MUTED} !important; font-size: 0.85rem !important; }}

/* Sidebar divider */
[data-testid="stSidebar"] hr {{ border-color: {SIDEBAR_BORDER}; }}

/* Main chat messages */
[data-testid="stChatMessage"] {{
    background-color: {CHAT_BG};
    border: 1px solid {CHAT_BORDER};
    border-radius: 12px;
    margin-bottom: 0.6rem;
}}

/* Chat input */
[data-testid="stChatInput"] textarea {{
    background-color: {CHAT_BG} !important;
    border: 1px solid {CHAT_BORDER} !important;
    color: {TEXT_PRIMARY} !important;
    border-radius: 12px !important;
}}

/* Main area text */
.stMarkdown, .stMarkdown p {{ color: {TEXT_PRIMARY}; }}

/* Spinner */
.stSpinner > div {{ border-top-color: #6366f1 !important; }}

/* Theme toggle button in header row */
.theme-toggle-btn {{
    margin-top: 2.8rem;
}}
.theme-toggle-btn button {{
    background: {THEME_BTN_BG} !important;
    color: {THEME_BTN_TEXT} !important;
    border: 1px solid {CARD_BORDER} !important;
    border-radius: 20px !important;
    font-size: 0.85rem !important;
    padding: 0.25rem 1rem !important;
    min-height: 2rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    transition: all 0.2s;
    float: right;
}}
.theme-toggle-btn button:hover {{
    box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
    border-color: #6366f1 !important;
}}

/* Feature cards */
.feature-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.feature-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.2);
}}
.feature-card .icon {{
    font-size: 2rem;
    background: {CARD_ICON_BG};
    border-radius: 12px;
    width: 54px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.8rem;
}}
.feature-card h4 {{
    color: {TEXT_PRIMARY};
    margin: 0 0 0.4rem 0;
    font-size: 1rem;
    font-weight: 600;
}}
.feature-card p {{
    color: {'#94a3b8' if is_dark else '#64748b'};
    margin: 0;
    font-size: 0.85rem;
    line-height: 1.5;
}}

/* Hero section */
.hero {{
    text-align: center;
    padding: 0.8rem 1rem 1rem;
}}
.hero h1 {{
    font-size: 2.4rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    margin-bottom: 0.5rem;
}}
.hero p {{
    font-size: 1.05rem;
    color: {'#94a3b8' if is_dark else '#64748b'};
    margin-bottom: 0;
}}
.hero .badge {{
    display: inline-block;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
    border-radius: 20px;
    padding: 2px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
}}

/* Step row */
.steps-row {{
    display: flex;
    gap: 0.5rem;
    align-items: center;
    justify-content: center;
    margin: 1.8rem 0 2.2rem;
    flex-wrap: wrap;
}}
.step-item {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.82rem;
    color: {'#94a3b8' if is_dark else '#64748b'};
}}
.step-num {{
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    flex-shrink: 0;
}}
.step-arrow {{ color: {'#2e3250' if is_dark else '#c8ccd8'}; font-size: 0.8rem; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ▶️ YouTube QA Agent")
    st.markdown(f"<p style='color:{SIDEBAR_MUTED}; font-size:0.85rem;'>Ask questions about any YouTube video using AI</p>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 🎬 Load Video")
    url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("⚡ Load Video", use_container_width=True):
        if not url.strip():
            st.warning("Please enter a YouTube URL.")
        else:
            with st.spinner("Fetching transcript and building vector store..."):
                from function_calling import load_video
                result = load_video.invoke({"url": url})
                if "✅" in result:
                    st.session_state.video_loaded = True
                    st.session_state.history.append(HumanMessage(content=f"Load this video: {url}"))
                    st.session_state.history.append(AIMessage(content=result))
                    st.success("Video loaded successfully!")
                else:
                    st.error(result)

    if st.session_state.video_loaded:
        st.divider()
        st.markdown("### ⚡ Actions")

        if st.button("📋 Summarize Video", use_container_width=True):
            with st.spinner("Generating summary..."):
                from function_calling import summarize_video
                summary = summarize_video.invoke({"placeholder": ""})
                summary = re.sub(r"<think>.*?</think>", "", summary, flags=re.DOTALL).strip()
                st.session_state.messages.append({"role": "assistant", "content": f"### 📋 Video Summary\n\n{summary}"})
                st.rerun()

        if st.button("🗺️ Create Mind Map", use_container_width=True):
            with st.spinner("Building mind map..."):
                from function_calling import create_mindmap
                raw = create_mindmap.invoke({"placeholder": ""})
                md_start = raw.find("#")
                mindmap_md = raw[md_start:].strip() if md_start != -1 else raw.strip()
                st.session_state.messages.append({"role": "assistant", "content": mindmap_md, "type": "mindmap"})
                st.rerun()

        st.divider()

        if _state["transcript"]:
            st.markdown("### 📊 Transcript Stats")
            transcript = _state["transcript"]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words", f"{len(transcript.split()):,}")
            with col2:
                st.metric("Chars", f"{len(transcript):,}")

        st.divider()
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
# Theme toggle — top-right of main content
_spacer, _btn_col = st.columns([11, 1])
with _btn_col:
    theme_label = "☀️" if is_dark else "🌙"
    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    if st.button(theme_label, key="theme_btn"):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.video_loaded:
    st.markdown('<div style="margin-top:-2.5rem">', unsafe_allow_html=True)
    # Hero
    st.markdown("""
    <div class="hero">
        <div class="badge">✦ AI-POWERED</div>
        <h1>YouTube QA Agent</h1>
        <p>Paste any YouTube URL, then ask questions, get summaries, and explore ideas — all powered by RAG.</p>
    </div>
    """, unsafe_allow_html=True)

    # How it works steps
    st.markdown("""
    <div class="steps-row">
        <div class="step-item"><div class="step-num">1</div> Paste URL</div>
        <div class="step-arrow">›</div>
        <div class="step-item"><div class="step-num">2</div> Load Video</div>
        <div class="step-arrow">›</div>
        <div class="step-item"><div class="step-num">3</div> Ask Questions</div>
        <div class="step-arrow">›</div>
        <div class="step-item"><div class="step-num">4</div> Get Answers</div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards row 1
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🎙️</div>
            <h4>Transcript Extraction</h4>
            <p>Automatically fetches the full video transcript using the YouTube API — no manual copy-paste needed.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🔍</div>
            <h4>Semantic Search</h4>
            <p>Transcript is chunked and embedded into a FAISS vector store for lightning-fast similarity search.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🤖</div>
            <h4>AI Question Answering</h4>
            <p>Ask anything about the video. The LLM answers using only the retrieved transcript context — no hallucinations.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Feature cards row 2
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📋</div>
            <h4>Video Summarization</h4>
            <p>Get a concise summary with key points highlighted — perfect when you're short on time.</p>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🗺️</div>
            <h4>Mind Map Generation</h4>
            <p>Visualize the video's concepts as an interactive mind map to quickly grasp the structure.</p>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">💬</div>
            <h4>Conversation Memory</h4>
            <p>Ask follow-up questions naturally. The agent remembers the full conversation history.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div style="margin-top:-2.5rem">', unsafe_allow_html=True)
    # Display conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "mindmap":
                st.markdown("### 🗺️ Mind Map")
                render_markmap(msg["content"], height=500, dark=is_dark)
            else:
                st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input("Ask a question about the video..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                st.session_state.history.append(HumanMessage(content=user_input))
                response = st.session_state.agent.invoke({"messages": st.session_state.history})
                ai_msg   = response["messages"][-1].content
                st.session_state.history.append(AIMessage(content=ai_msg))

                # Detect if the response is a mind map (contains markdown heading structure)
                is_mindmap = ai_msg.find("#") != -1 and "mind map" in user_input.lower()
                if is_mindmap:
                    md_start = ai_msg.find("#")
                    mindmap_md = ai_msg[md_start:].strip()
                    st.session_state.messages.append({"role": "assistant", "content": mindmap_md, "type": "mindmap"})
                    st.markdown("### 🗺️ Mind Map")
                    render_markmap(mindmap_md, height=500, dark=is_dark)
                else:
                    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                    st.markdown(ai_msg)

    st.markdown('</div>', unsafe_allow_html=True)