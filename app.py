import streamlit as st
from dotenv import load_dotenv
from rag_engine import MdRag 

load_dotenv()

st.set_page_config(
    page_title="Markdown AI Asistant",
    page_icon="✨",
    layout="centered"
)

st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {s
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
    .stChatMessage {
        background-color: transparent;
        border: none;
    }
    
    /* User Message Bubble - Blue Gradient */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(28, 33, 40, 0.5);
        border: 1px solid rgba(79, 172, 254, 0.2);
        border-radius: 15px;
        padding: 10px;
    }

    /* Assistant Message Bubble - Subtle Dark */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
    }

    /* Input Box Styling */
    .stTextInput input {
        border-radius: 20px;
        border: 1px solid #333;
        background-color: #161b22;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---

@st.cache_resource
def get_rag_system():
    """
    Initialize the RAG system once and cache it.
    This prevents reloading the model on every interaction.
    """
    return MdRag("test.md")

def main():
    st.title("Markdown AI Assistant")
    st.markdown("Ask questions about your Markdown File.")

    try:
        rag = get_rag_system()
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {e}")
        st.info("Please ensure 'rag_engine.py' is in the same directory.")
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