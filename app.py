import streamlit as st
import os
from dotenv import load_dotenv
import csv
import datetime
from rag_engine import MdRag 

load_dotenv()

st.set_page_config(
    page_title="RAG MD",
    page_icon="🌍",
    layout="centered"
)

st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Header Styling */
    h1 {
        background: -webkit-linear-gradient(45deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Chat Bubble Styling */
    div[data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
    }
    
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(28, 33, 40, 0.5);
        border: 1px solid rgba(79, 172, 254, 0.2);
    }

    .source-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #4facfe;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.9em;
    }
    .source-header {
        font-weight: bold;
        color: #4facfe;
        margin-bottom: 5px;
    }

    /* Transparent buttons for Feedback (Main Area only) */
    section[data-testid="stMain"] .stButton button {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 1.5rem;
        box-shadow: none !important;
    }
    section[data-testid="stMain"] .stButton button:hover {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transform: scale(1.2);
    }
    section[data-testid="stMain"] .stButton button:focus {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    section[data-testid="stMain"] .stButton button:active {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)


SOURCE_DIR = "llm_sources"



@st.cache_resource
def get_rag_system():
    return MdRag(temperature=0.3)

def log_feedback(question, answer, rating):
    feedback_dir = "feedback"
    if not os.path.exists(feedback_dir):
        os.makedirs(feedback_dir)
        
    feedback_file = os.path.join(feedback_dir, "feedback.csv")
    file_exists = os.path.isfile(feedback_file)
    
    with open(feedback_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Question", "Answer", "Rating"])
        
        writer.writerow([datetime.datetime.now(), question, answer, rating])

def main():
    with st.sidebar:
        if os.getenv("GOOGLE_API_KEY"):
            st.success("Using Gemini")
        else:
            st.info("Using Ollama")
        
        st.divider()
        
        st.header("Knowledge Base")
        st.write(f"Source: `{SOURCE_DIR}`")
        
        if st.button("Sync Knowledge Base"):
            with st.spinner("Syncing database..."):
                # Clear cache to force reload and trigger incremental indexing
                st.cache_resource.clear()
                st.success("Database synced.")
                st.rerun()
            
        st.divider()
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    st.title("Chat with your Knowledge Base ")

    try:
        rag = get_rag_system()
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {e}")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []



    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("Sources Used"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {i+1}**")
                        st.markdown(source)
                        st.divider()

    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = rag.query(prompt)
                
                sources_text = []
                if isinstance(response, dict):
                    answer = response["answer"]
                    sources = response["sources"]
                else:
                    answer = response
                    sources = []

                st.markdown(answer)
                
                if sources:
                    with st.expander("Sources Used"):
                        for i, doc in enumerate(sources):
                            # Use original_content if available, else page_content
                            content = doc.metadata.get("original_content", doc.page_content)
                            sources_text.append(content)
                            
                            st.markdown(f"""
                            <div class="source-box">
                                <div class="source-header">Source {i+1}</div>
                                {content}
                            </div>
                            """, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources_text})
        st.rerun()

    # Render feedback buttons for the last assistant message if it exists
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_msg = st.session_state.messages[-1]
        # We need to find the corresponding user question (usually the one before)
        if len(st.session_state.messages) >= 2:
            last_question = st.session_state.messages[-2]["content"]
            
            # Use tight columns for buttons to keep them adjacent
            col1, col2, col3, _ = st.columns([0.1, 0.1, 0.1, 1])
            with col1:
                if st.button("👍", key="thumbs_up"):
                    log_feedback(last_question, last_msg["content"], "Positive")
                    st.toast("Thanks for your feedback!")
            with col2:
                if st.button("👎", key="thumbs_down"):
                    log_feedback(last_question, last_msg["content"], "Negative")
                    st.toast("Thanks for your feedback!")
            with col3:
                if st.button("📋", key="copy_response"):
                    # Use st.code to enable copy functionality
                    st.code(last_msg["content"], language=None)
                    st.toast("Response ready to copy!")

if __name__ == "__main__":
    main()