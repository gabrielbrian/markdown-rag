import streamlit as st
import os
from dotenv import load_dotenv
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
</style>
""", unsafe_allow_html=True)


SOURCE_DIR = "llm_sources"



@st.cache_resource
def get_rag_system():
    return MdRag(temperature=0.3)

def main():
    with st.sidebar:
        if os.getenv("GOOGLE_API_KEY"):
            st.success("Using Gemini")
        else:
            st.info("Using Ollama")
        
        st.divider()
        
        st.header("Knowledge Base")
        st.write(f"Source: `{SOURCE_DIR}`")
        
        if st.button("Rebuild Knowledge Base"):
            with st.spinner("Rebuilding database..."):
                # Clear existing DB
                if os.path.exists("./chroma_db"):
                    import shutil
                    shutil.rmtree("./chroma_db")
                
                # Clear cache to force reload
                st.cache_resource.clear()
                st.success("Database cleared. Reloading...")
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