# Local RAG Implementation Guide

A local Retrieval-Augmented Generation (RAG) system for Markdown and Text files. It features a **Multi-File Knowledge Base**, **Hierarchical Context Preservation**, and **LLM-Generated Question Augmentation**.

## Features
- **Multi-File Support**: Ingests all `.md` and `.txt` files from the `llm_sources` directory.
- **Dual LLM Support**: Automatically switches between **Ollama** (Local) and **Google Gemini** (Cloud) based on configuration.
- **Context Enrichment**: Enhances retrieval by generating "succinct context" and "potential questions" for each chunk using an LLM.

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
2.  **Rebuild Knowledge Base**: If you add/remove files or change the LLM provider, click the **"Rebuild Knowledge Base"** button in the sidebar to re-process everything.

## Tuning
- **Chunk Size**: Adjusted in `preprocess.py` (default: 2000 chars for MD).
- **Temperature**: Adjusted in `rag_engine.py` (default: 0.5).
- **Retrieval Count (k)**: Adjusted in `rag_engine.py` (default: 5 chunks).