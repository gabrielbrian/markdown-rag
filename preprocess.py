import os
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".md":
        return _split_markdown(text)
    
    elif file_extension == ".txt":
        return _split_text(text)
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only .md and .txt are supported.")

def _split_markdown(text):
  
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
        ("######", "Header 6"),
    ]
    
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_splits = md_splitter.split_text(text)

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return char_splitter.split_documents(md_splits)

def _split_text(text):
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""] 
    )
    return char_splitter.create_documents([text])