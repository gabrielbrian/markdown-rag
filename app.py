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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

    /* Main Background and Text */
    .stApp {
        background-color: #FDFBF7; /* Cream/Old Book Paper */
        color: #2C3E50; /* Dark Charcoal */
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Styling */
    h1 {
        color: #2C3E50;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        background: none;
        -webkit-text-fill-color: initial;
    }

    /* Chat Bubble Styling */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* User Message - Pastel Blue */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
        color: #1565C0;
    }

    /* Assistant Message - White/Clean */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        color: #37474F;
        position: relative;
    }

    /* Source Box - Note Card Style */
    .source-box {
        background-color: #FFF9C4; /* Pastel Yellow */
        border: 1px solid #FFF59D;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.85em;
        color: #5D4037;
    }
    .source-header {
        font-weight: bold;
        color: #FBC02D;
        margin-bottom: 5px;
        text-transform: uppercase;
        font-size: 0.75em;
        letter-spacing: 1px;
    }

    /* Hide Chat Avatars */
    div[data-testid="stChatMessage"] > div:first-child {
        display: none;
    }
    
    /* Adjust message padding since avatar is gone */
    div[data-testid="stChatMessage"] {
        padding-left: 20px;
        padding-right: 20px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F9F7F1; /* Slightly darker cream */
        border-right: 1px solid #E0E0E0;
    }


    /* Input Area Styling - Keep it simple */
    div[data-testid="stBottom"] {
        background-color: #FDFBF7;
    }
    
    /* Chat Input Box - Basic styling only */
    div[data-testid="stChatInput"] textarea {
        border: 1px solid #D7CCC8;
        border-radius: 20px;
        padding-left: 20px;
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE/Edge */
    }
    
    /* Hide scrollbar (Chrome/Safari/Webkit) */
    div[data-testid="stChatInput"] textarea::-webkit-scrollbar {
        width: 0;
        height: 0;
    }
    
    /* Header Styling (Streamlit's top bar) */
    header[data-testid="stHeader"] {
        background-color: #FDFBF7;
    }

    /* --- IN-MESSAGE BUTTON STYLING --- */
    
    /* Reset all buttons inside chat messages to be transparent and icon-like */
    div[data-testid="stChatMessage"] button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        color: #90A4AE !important;
        transition: all 0.2s ease;
        height: auto !important;
        min-height: 0px !important;
    }

    /* Hover Effects */
    div[data-testid="stChatMessage"] button:hover {
        color: #2C3E50 !important;
        transform: scale(1.1);
        background-color: transparent !important;
    }

    /* Specific Styling using Title attributes (Help Text) */
    
    /* Feedback Icons (✔ and ✘) */
    button[title="Helpful"], button[title="Not Helpful"] {
        font-size: 1.4rem !important;
        line-height: 1 !important;
        margin-top: 10px;
    }

    /* Copy Button */
    button[title="Copy to clipboard"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #B0BEC5 !important;
        display: flex;
        justify-content: flex-end;
    }
    button[title="Copy to clipboard"]:hover {
        color: #546E7A !important;
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

    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            is_last_assistant_message = (i == len(st.session_state.messages) - 1) and (message["role"] == "assistant")
            
            if is_last_assistant_message:
                st.markdown(message["content"])
                
                if "sources" in message and message["sources"]:
                    with st.expander("Sources Used"):
                        for idx, source in enumerate(message["sources"]):
                            st.markdown(f"**Source {idx+1}**")
                            st.markdown(source)
                            st.divider()
                
                last_question = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "Unknown"
                
                fb_col1, fb_col2, fb_spacer, fb_copy = st.columns([0.08, 0.08, 0.69, 0.08])
                with fb_col1:
                    if st.button("✔", key=f"thumbs_up_{i}", help="Helpful"):
                        log_feedback(last_question, message["content"], "Positive")
                        st.toast("Thanks for your feedback!")
                with fb_col2:
                    if st.button("✘", key=f"thumbs_down_{i}", help="Not Helpful"):
                        log_feedback(last_question, message["content"], "Negative")
                        st.toast("Thanks for your feedback!")
                with fb_copy:
                    if st.button("Copy", key=f"copy_{i}", help="Copy to clipboard"):
                        st.code(message["content"], language=None)
                        st.toast("Response ready to copy!")

            else:
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    with st.expander("Sources Used"):
                        for idx, source in enumerate(message["sources"]):
                            st.markdown(f"**Source {idx+1}**")
                            st.markdown(source)
                            st.divider()

    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = st.session_state.messages[-1]["content"]
                response = rag.query(prompt)
                
                sources_text = []
                if isinstance(response, dict):
                    answer = response["answer"]
                    sources = response["sources"]
                else:
                    answer = response
                    sources = []

                for doc in sources:
                    content = doc.metadata.get("original_content", doc.page_content)
                    sources_text.append(content)
        
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources_text})
        st.rerun()

if __name__ == "__main__":
    main()