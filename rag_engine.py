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

from langchain_google_genai import ChatGoogleGenerativeAI

class MdRag:
    def __init__(self, source_dir="llm_sources", temperature=0.5, persist_dir="./chroma_db"):

        self.source_dir = source_dir
        self.temperature = temperature
        self.persist_dir = persist_dir
        
        self.vectorstore = None
        self.chain = None
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            print("Using Gemini Model")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=self.temperature,
                google_api_key=api_key
            )
        else:
            print("Using Ollama Model")
            self.llm = ChatOllama(
                model="phi3:mini",
                temperature=self.temperature
            )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1.5",
            model_kwargs={
                'device': 'cpu', 
                'trust_remote_code': True
            }
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
        print(f"Scanning {self.source_dir}...")
        
        all_docs = []
        
        if not os.path.exists(self.source_dir):
            os.makedirs(self.source_dir)
            print(f"Created directory {self.source_dir}")
            return

        files = [f for f in os.listdir(self.source_dir) if f.endswith(('.md', '.txt'))]
        
        if not files:
            print("No files found to ingest.")
            return

        for filename in files:
            file_path = os.path.join(self.source_dir, filename)
            print(f"Processing {file_path}...")
            
            try:
                docs = process_document(file_path, llm=self.llm)
                all_docs.extend(docs)
                print(f"  - Generated {len(docs)} chunks.")
            except Exception as e:
                print(f"  - Error processing {filename}: {e}")

        if not all_docs:
            print("No chunks generated from any files.")
            return

        print(f"\nTotal chunks to ingest: {len(all_docs)}")

        self.vectorstore = Chroma.from_documents(
            documents=all_docs,
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