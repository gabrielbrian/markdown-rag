import os
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_document(file_path, llm=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".md":
        return _split_markdown(text, llm, file_path)
    
    elif file_extension == ".txt":
        return _split_text(text)
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only .md and .txt are supported.")

def _split_markdown(text, llm=None, file_path=None):
  
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
        chunk_size=2000,
        chunk_overlap=200
    )
    docs = char_splitter.split_documents(md_splits)

    section_chunks = {}
    for doc in docs:
        section_key = tuple((k, v) for k, v in sorted(doc.metadata.items()) if k.startswith("Header"))
        if section_key not in section_chunks:
            section_chunks[section_key] = []
        section_chunks[section_key].append(doc)
    
    filtered_docs = []
    for doc in docs:
        # Skip chunks with minimal content (less than 50 chars after stripping)
        if len(doc.page_content.strip()) < 50:
            continue
            
        section_key = tuple((k, v) for k, v in sorted(doc.metadata.items()) if k.startswith("Header"))
        chunks_in_section = section_chunks[section_key]
        
        location_parts = []
        
        if file_path:
            location_parts.append(file_path)
        
        for header_name in ["Header 1", "Header 2", "Header 3", "Header 4", "Header 5", "Header 6"]:
            if header_name in doc.metadata:
                location_parts.append(doc.metadata[header_name])
        
        header_context = ""
        
        if location_parts:
            breadcrumb = " / ".join(location_parts)
            header_context += f"Location: {breadcrumb}\n\n"
        
        if len(chunks_in_section) > 1:
            chunk_index = chunks_in_section.index(doc) + 1
            total_chunks = len(chunks_in_section)
            header_context += f"[Section split: Part {chunk_index} of {total_chunks}]\n\n"
        
        if llm:
            try:
                prompt = f"Here is a section of text:\n{doc.page_content}\n\nWhat questions could a user ask to find this section? Return only the possible questions."
                questions = llm.invoke(prompt).content
                header_context += f"Potential Questions:\n{questions}\n\n"
            except Exception as e:
                print(f"Error generating questions: {e}")

        if header_context:
            doc.page_content = f"{header_context}---CONTENT---\n\n{doc.page_content}"
        
        filtered_docs.append(doc)
            
    return filtered_docs

def _split_text(text):
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""] 
    )
    return char_splitter.create_documents([text])