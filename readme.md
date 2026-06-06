# 🎬 YouTube QA Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/LangGraph-Agent-6366f1?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-Qwen3--32b-00A67E?style=for-the-badge"/>
</p>

<p align="center">
  An AI-powered agent that lets you ask questions, get summaries, and generate mind maps from any YouTube video — built with RAG, LangGraph, and Streamlit.
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Transcript Extraction** | Automatically fetches YouTube video transcripts |
| 🔍 **Semantic Search** | Chunks and embeds transcripts into ChromaDB for similarity search |
| 🤖 **Question Answering** | Answers questions strictly from the video — no hallucinations |
| 📋 **Summarization** | Generates a concise summary with key bullet points |
| 🗺️ **Mind Map** | Creates an interactive visual mind map of the video content |
| 💬 **Conversation Memory** | Supports natural follow-up questions across multiple turns |

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **LLM** | Groq — Qwen3-32b |
| **Agent** | LangGraph `create_react_agent` |
| **RAG** | LangChain + ChromaDB + HuggingFace Embeddings |
| **Transcript** | YouTube Transcript API |
| **UI** | Streamlit |
| **Validation** | Pydantic |

---

## 🚀 Setup

**1. Clone the repository**
```bash
git clone https://github.com/your-username/youtube-qa-agent.git
cd youtube-qa-agent
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure your API key**
```bash
cp .env.example .env
```
Then edit `.env` and add your [Groq API key](https://console.groq.com/).

---

## ▶️ Run

```bash
streamlit run app.py
```

---

## 📖 Usage

1. Paste a YouTube URL in the sidebar and click **Load Video**
2. Ask questions in the chat input
3. Use sidebar buttons to **Summarize** or generate a **Mind Map**

---

## 📁 Project Structure

```
youtube-qa-agent/
├── app.py                 # Streamlit UI
├── function_calling.py    # LangGraph agent + tools
├── rag_pipeline.py        # ChromaDB vector store & retriever
├── transcript.py          # YouTube transcript extraction
├── requirements.txt
├── .env.example
└── .streamlit/
    └── config.toml
```
