# Local RAG Implementation Guide

A local Retrieval-Augmented Generation (RAG) system for Markdown files with preprocessing, hierarchical context preservation, and LLM-generated question augmentation.

## Prerequisites

- Python 3.8 or later
- Ollama installed locally

## Set up your environment

### Create and activate a virtual environment

1. Create the virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the environment:
   - **macOS/Linux**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configure your content

1. Place your Markdown file in the project folder.

2. In `rag_engine.py`, update the filename from `test.md` to your filename.

### Set up the AI model

1. Download and install Ollama from [ollama.com](https://ollama.com).

2. Pull the model:
   ```bash
   ollama pull phi3:mini
   ```
   You can use a different model if you prefer.

3. If you're not using `phi3:mini`, update the model name in `rag_engine.py` at line 27:
   ```python
   llm = ChatOllama(
       model="your-model-name",  # Update this line
       temperature=0
   )
   ```

4. Make sure Ollama is running in the background.

## Run the application

With your virtual environment active, run:
```bash
streamlit run app.py
```

The application opens in a new browser tab with a chat interface connected to your Markdown file.


## Tune the system

### chunk_size (in preprocess.py)
- **Current settings**: 2,000 characters for Markdown files, 1,000 characters for text files
- **Smaller (500-1,000)**: Use for specific fact retrieval (for example, "What is the IP address?")
- **Larger (1,500-2,000)**: Use for summaries or broad concept questions
- **Note**: Markdown files use larger chunks to keep sections together when possible.

### chunk_overlap
Keep this value at 10-20% of your chunk size (currently 200 characters). This prevents sentences from being cut in half at chunk boundaries.

### temperature (in rag_engine.py)
- **0**: Use for technical documentation and RAG. This forces the AI to stick to facts.
- **0.7 or higher**: Use for creative writing or brainstorming.

### k (retrieval count in rag_engine.py)
- **Current setting**: 5 chunks retrieved per query
- **Lower (2-3)**: Provides faster, more focused answers
- **Higher (7-10)**: Provides more comprehensive context, but may include less relevant information