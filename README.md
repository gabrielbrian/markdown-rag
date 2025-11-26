# Local RAG Implementation Guide

A local Retrieval-Augmented Generation (RAG) system for Markdown and Text files. It features a **Multi-File Knowledge Base**, **Hierarchical Context Preservation**, **LLM-Generated Question Augmentation**, and **High-Performance Async Ingestion**.

## Features
- **Multi-File Support**: Ingests all `.md` and `.txt` files from the `llm_sources` directory.
- **Dual LLM Support**: Automatically switches between **Ollama** (Local) and **Google Gemini** (Cloud) based on configuration.
- **Advanced Context Enrichment**:
    - **Hierarchical Breadcrumbs**: Preserves file path and header structure (e.g., `File > Header 1 > Header 2`).
    - **Global Document Summary**: Generates a summary of the entire file *once* to provide high-level context for every chunk (optimizes token usage).
    - **Potential Questions**: Generates questions that a user might ask to find specific chunks.
- **"Clean Text" Citations**: Uses enriched metadata for high-accuracy retrieval but displays the original, clean text to the user in the "Sources Used" section.
- **High-Performance Ingestion**: Uses `asyncio` and parallel processing to enrich document chunks concurrently, significantly reducing ingestion time.

## Prerequisites
- Python 3.8 or later
- [Ollama](https://ollama.com) installed locally (for local mode)

## Setup

### 1. Environment Setup
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Content
Place your Markdown (`.md`) or Text (`.txt`) files in the `llm_sources/` directory. The system will ingest all of them.

### 3. Configure LLM Provider
The system supports two modes. It auto-detects which one to use based on your environment variables.

#### Option A: Use Google Gemini (Recommended for speed/quality)
1.  Get an API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create a `.env` file in the project root:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```
3.  The app will automatically detect the key and use Gemini.

#### Option B: Use Ollama (Local/Private)
1.  Ensure you have no `.env` file (or comment out the key).
2.  Pull the default model:
    ```bash
    ollama pull gemma3:4b
    ```
3.  The app will default to Ollama if no API key is found.

## Run the Application
```bash
streamlit run app.py
```

## Usage
1.  **Chat**: Ask questions about your documents. The system searches across all files in `llm_sources`.
2.  **View Sources**: Expand the "Sources Used" section in the chat to see the exact text blocks used to generate the answer.
3.  **Rebuild Knowledge Base**: If you add/remove files or change the LLM provider, click the **"Rebuild Knowledge Base"** button in the sidebar to re-process everything.

## Architecture & Optimizations
- **Async Pipeline**: The ingestion process (`preprocess.py` and `rag_engine.py`) is fully asynchronous, utilizing `asyncio.gather` to process chunks in parallel.
- **Rate Limiting**: Implements `asyncio.Semaphore` to limit concurrent LLM requests (default: 5), preventing API rate limits (HTTP 429) and local resource exhaustion.
- **Token Optimization**: Instead of passing the full document text to the LLM for every chunk's context generation, we generate a **Global Summary** once per file and pass that summary to the chunk enrichment prompt. This reduces token usage by ~90% for large files.
- **Metadata Separation**: Enriched context (breadcrumbs, questions, summary) is prepended to the text for the embedding model but separated by `---CONTENT---`. The UI intelligently hides this metadata to keep citations clean.

## Tuning
- **Chunk Size**: Adjusted in `preprocess.py` (default: 2000 chars for MD).
- **Temperature**: Adjusted in `rag_engine.py` (default: 0.5).
- **Retrieval Count (k)**: Adjusted in `rag_engine.py` (default: 5 chunks).