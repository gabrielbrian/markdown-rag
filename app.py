import streamlit as st
import os
from dotenv import load_dotenv
from rag_engine import MdRag 

load_dotenv()

st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="✨",
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
</style>
""", unsafe_allow_html=True)


SOURCE_DIR = "llm_sources"

def get_available_files():
    """Scans the source directory for .md and .txt files."""
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)
        return []
    return [f for f in os.listdir(SOURCE_DIR) if f.endswith(('.md', '.txt'))]

@st.cache_resource
def get_rag_system(filename):

    return MdRag(filename=filename, temperature=0.3)

def main():
    with st.sidebar:
        st.header("🗂️ Document Selection")
        
        files = get_available_files()
        if not files:
            st.warning(f"No files found in '{SOURCE_DIR}' folder.")
            st.stop()
            
        selected_file = st.selectbox("Choose a file:", files)
        
        st.divider()
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    st.title(f"Chat with {selected_file}")

    try:
        rag = get_rag_system(selected_file)
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {e}")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_file" not in st.session_state:
        st.session_state.current_file = selected_file
    elif st.session_state.current_file != selected_file:
        st.session_state.messages = [] # Clear history on change
        st.session_state.current_file = selected_file
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = rag.query(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()