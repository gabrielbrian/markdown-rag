import os
import sys
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from preprocess import process_document

load_dotenv()

class MdRag:
    def __init__(self, filename, source_dir="llm_sources", temperature=0):

        self.source_dir = source_dir
        self.file_path = os.path.join(self.source_dir, filename)
        self.temperature = temperature
        
        self.vectorstore = None
        self.chain = None
        
        self._ingest_and_index()

    def _ingest_and_index(self):
        print(f"Processing {self.file_path}...")
        
        try:
            final_docs = process_document(self.file_path)
            print(f"Generated {len(final_docs)} chunks.")
        except Exception as e:
            print(f"Error processing file: {e}")
            return

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
            temperature=self.temperature
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
            return "System not initialized or file processing failed."
        return self.chain.invoke(question)