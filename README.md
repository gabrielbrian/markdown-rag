## Local RAG Implementation Guide

A simple local RAG implementation over Markdown files using LangChain, Ollama, and Streamlit.

### 1. Environment Setup 

1. **Create the virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the environment:**
   - **Mac/Linux:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 2. Content Setup

1. Place your Markdown file in the project folder.

2. Update the filename in `rag_engine.py` *Change "test.md" to your filename.*

## 3. AI Model Setup

1. **Install Ollama:** Download from [ollama.com](https://ollama.com).

2. **Pull a model:** Open your terminal and run:
   ```bash
   ollama pull phi3:mini
   ```
   Or whichever model you prefer

3. **Update the Code:**
   If you are NOT using `phi3:mini`, open `rag_engine.py` and update line 64:
   ```python
   llm = ChatOllama(
       model="your-model-name",  # <- Update this
       temperature=0
   )
   ```

4. **Ensure Ollama is running:** Make sure the Ollama app is open in the background.

## 4. Run the App

With your virtual environment still active:
```bash
streamlit run app.py
```

A new browser tab will open with the chat box connected to your Markdown file. 

## Quick Guide on Tuning

#### `chunk_size`
- **Smaller (500):** Good for specific fact retrieval ("What is the IP address?").
- **Larger (e.g., 2000):** Good for summaries or answering broad concept questions.

#### `chunk_overlap`
Keep this around 10-20% of your chunk size. It prevents sentences from getting cut in half at the edge of a chunk.

#### `temperature`
- **`0`:** Best for technical docs and RAG. It forces the AI to stick to the facts.
- **`0.7`+:** Better for creative writing or brainstorming.