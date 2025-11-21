import os
import sys
from dotenv import load_dotenv

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables (useful if running this file directly)
load_dotenv()

class MdRag:
    def __init__(self, filename="test.md"):
        self.file_path = filename
        self.vectorstore = None
        self.chain = None
        
        # Ensure dummy file exists for demo purposes
        if not os.path.exists(self.file_path):
            print(f"File {self.file_path} not found. Creating placeholder.")
            with open(self.file_path, "w") as f:
                f.write("# Welcome\nThis is a placeholder file for the RAG system.")

        self._ingest_and_index()

    def _ingest_and_index(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_splits = md_splitter.split_text(text)

        char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        final_docs = char_splitter.split_documents(md_splits)

        # Using CPU for embeddings to ensure compatibility
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        self.vectorstore = InMemoryVectorStore(embeddings)
        self.vectorstore.add_documents(final_docs)
        
        self._build_chain()

    def _build_chain(self):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        llm = ChatOllama(
            model="phi3:mini",
            temperature=0
        )

        system_prompt = (
            "You are the expert support assistant "
            "Use the following context to answer the user's question. "
            "Be concise, helpful, and only give relevant information. "
            "If the answer is not in the provided content, say you don't know.\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        self.chain = (
            {
                "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
                "input": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    def query(self, question):
        if not self.chain:
            return "System not initialized."
        return self.chain.invoke(question)

if __name__ == "__main__":
    # Test the logic independently
    rag = MdRag()
    print(rag.query("Hello"))