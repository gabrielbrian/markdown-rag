import os
import sys
import asyncio
import json
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
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
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
            print(f"Using Gemini Model: {model_name}")
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=self.temperature,
                google_api_key=api_key
            )
        else:
            model_name = os.getenv("OLLAMA_MODEL", "gemma3:4b")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            print(f"Using Ollama Model: {model_name} at {base_url}")
            self.llm = ChatOllama(
                model=model_name,
                temperature=self.temperature,
                base_url=base_url
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
        
        self._ingest_and_index()
        
        self._build_chain()

    def _ingest_and_index(self):
        asyncio.run(self._ingest_and_index_async())

    async def _ingest_and_index_async(self):
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

        hashes_file = os.path.join(self.source_dir, "file_hashes.json")
        existing_hashes = {}
        if os.path.exists(hashes_file):
            try:
                with open(hashes_file, "r") as f:
                    existing_hashes = json.load(f)
            except Exception:
                print("Could not load existing hashes. Re-indexing all.")

        new_hashes = existing_hashes.copy()
        files_to_process = []

        from preprocess import calculate_file_hash
        
        for filename in files:
            file_path = os.path.join(self.source_dir, filename)
            current_hash = calculate_file_hash(file_path)
            
            if filename in existing_hashes and existing_hashes[filename] == current_hash:
                print(f"Skipping {filename} (unchanged).")
            else:
                files_to_process.append(filename)
                new_hashes[filename] = current_hash

        if not files_to_process:
            print("No files changed. Knowledge base is up to date.")
            return

        print(f"Processing {len(files_to_process)} changed files...")

        for filename in files_to_process:
            file_path = os.path.join(self.source_dir, filename)
            print(f"Processing {file_path}...")
            
            try:
                docs = await process_document(file_path, llm=self.llm)
                all_docs.extend(docs)
                print(f"  - Generated {len(docs)} chunks.")
            except Exception as e:
                print(f"  - Error processing {filename}: {e}")

        if not all_docs:
            print("No chunks generated from changed files.")

            if files_to_process:
                 with open(hashes_file, "w") as f:
                    json.dump(new_hashes, f)
            return

        print(f"\nTotal new chunks to ingest: {len(all_docs)}")

        if self.vectorstore:
            print("Adding to existing vector store...")
            self.vectorstore.add_documents(all_docs)
        else:
            print("Creating new vector store...")
            self.vectorstore = Chroma.from_documents(
                documents=all_docs,
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
        
        print(f"Vector store persisted to {self.persist_dir}")
        
        with open(hashes_file, "w") as f:
            json.dump(new_hashes, f)

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
            RunnableParallel({"context": retriever, "input": RunnablePassthrough()})
            | {
                "answer": (
                    {
                        "context": (lambda x: "\n\n".join(d.page_content for d in x["context"])),
                        "input": lambda x: x["input"]
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                ),
                "sources": lambda x: x["context"]
            }
        )

    def query(self, question):
        if not self.chain:
            return "System not initialized or file processing failed."
        try:
            return self.chain.invoke(question)
        except Exception as e:
            error_str = str(e)
            if "Connection refused" in error_str or "Network is unreachable" in error_str or "Errno 101" in error_str:
                return ("Error connecting to LLM")
            raise e