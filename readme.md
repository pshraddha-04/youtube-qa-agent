# YouTube QA Agent

An AI-powered agent that lets you ask questions, get summaries, and generate mind maps from any YouTube video — built with RAG, LangGraph, and Streamlit.

## Features

- **Transcript Extraction** — Fetches YouTube video transcripts automatically
- **RAG Pipeline** — Chunks and embeds transcripts into ChromaDB for semantic search
- **Question Answering** — Answers questions strictly from the video transcript
- **Summarization** — Generates a concise summary with key bullet points
- **Mind Map** — Creates an interactive visual mind map of the video content
- **Conversation Memory** — Supports follow-up questions across multiple turns

## Tech Stack

Python, LangChain, LangGraph, ChromaDB, HuggingFace Embeddings, Groq (Qwen3-32b), Streamlit, YouTube Transcript API, Pydantic

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/youtube-qa-agent.git
   cd youtube-qa-agent
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your API key
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your [Groq API key](https://console.groq.com/).

## Run

```bash
streamlit run app.py
```

## Usage

1. Paste a YouTube URL in the sidebar and click **Load Video**
2. Ask questions in the chat input
3. Use sidebar buttons to **Summarize** or generate a **Mind Map**
