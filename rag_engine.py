import os
import sys
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from preprocess import process_document

load_dotenv()

class MdRag:
    def __init__(self, filename, source_dir="llm_sources", temperature=0.5, persist_dir="./chroma_db"):

        self.source_dir = source_dir
        self.file_path = os.path.join(self.source_dir, filename)
        self.temperature = temperature
        self.persist_dir = persist_dir
        
        self.vectorstore = None
        self.chain = None
        
        self.llm = ChatOllama(
            model="phi3:mini",
            temperature=self.temperature
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            print(f"Loading existing vector database from {self.persist_dir}...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        else:
            print("No existing database found. Building new vector store...")
            self._ingest_and_index()
        
        self._build_chain()

    def _ingest_and_index(self):
        print(f"Processing {self.file_path}...")
        
        try:
            final_docs = process_document(self.file_path, llm=self.llm)
            print(f"Generated {len(final_docs)} chunks.")
            
            print("\n--- Generated Chunks Preview ---")
            for i, doc in enumerate(final_docs):
                print(f"\nChunk {i+1}:")
                print(doc.page_content)
                print("-" * 40)
            print("--- End of Chunks Preview ---\n")

        except Exception as e:
            print(f"Error processing file: {e}")
            return

        self.vectorstore = Chroma.from_documents(
            documents=final_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print(f"Vector store persisted to {self.persist_dir}")

    def _build_chain(self):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        system_prompt = (
            "You are an expert support assistant. Use the following context to answer the user's question.\n\n"
            "<context>\n"
            "{context}\n"
            "</context>\n\n"
            "Note: Content inside <context> includes location metadata and potential questions above '---CONTENT---'. "
            "Use this metadata to understand document structure and relevance, but answer only using the text below '---CONTENT---'. "
            "Be concise, helpful, and only give relevant information. "
            "If the answer is not in the content section, say you don't know."
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
            | self.llm
            | StrOutputParser()
        )

    def query(self, question):
        if not self.chain:
            return "System not initialized or file processing failed."
        return self.chain.invoke(question)