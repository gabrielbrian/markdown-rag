import os
import asyncio
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

async def process_document(file_path, llm=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".md":
        return await _split_markdown(text, llm, file_path)
    
    elif file_extension == ".txt":
        return _split_text(text)
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only .md and .txt are supported.")

async def _generate_global_summary(text, llm):
    if not llm:
        return ""
    
    # Truncate text for summary generation if it's too long to avoid context window issues
    # Taking first 10k chars should be enough for a high-level summary
    truncated_text = text[:10000]
    
    prompt = (
        f"<document>\n{truncated_text}\n</document>\n"
        "Please provide a concise global summary (3-4 sentences) of this document. "
        "This summary will be used to provide context for individual chunks."
    )
    try:
        response = await llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating global summary: {e}")
        return ""

async def _enrich_chunk(doc, global_summary, llm, semaphore):
    if not llm:
        return doc

    async with semaphore:
        try:
            # 1. Generate Contextual Context using Global Summary
            context_prompt = (
                f"Global Document Summary:\n{global_summary}\n\n"
                f"Chunk Content:\n{doc.page_content}\n\n"
                "Based on the global summary, provide a short, succinct context to situate this chunk within the document. "
                "Answer only with the succinct context."
            )
            
            # 2. Generate Questions
            questions_prompt = (
                f"Chunk Content:\n{doc.page_content}\n\n"
                "What questions could a user ask to find this section? Return only the possible questions."
            )

            # Run both LLM calls in parallel for this chunk
            chunk_context_res, questions_res = await asyncio.gather(
                llm.ainvoke(context_prompt),
                llm.ainvoke(questions_prompt)
            )
            
            chunk_context = chunk_context_res.content
            questions = questions_res.content
            
            enrichment = f"Context:\n{chunk_context}\n\nPotential Questions:\n{questions}\n\n"
            return enrichment
            
        except Exception as e:
            print(f"Error enriching chunk: {e}")
            return ""

async def _split_markdown(text, llm=None, file_path=None):
  
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
    
    # Generate Global Summary once
    global_summary = ""
    if llm:
        print("Generating global document summary...")
        global_summary = await _generate_global_summary(text, llm)
        print("Global summary generated.")

    tasks = []
    processed_docs = []
    
    # Limit concurrency to 5 to avoid rate limits or crashing local LLMs
    semaphore = asyncio.Semaphore(5)

    for doc in docs:
        # Skip chunks with minimal content
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
        
        structural_context = ""
        if location_parts:
            breadcrumb = " / ".join(location_parts)
            structural_context += f"Location: {breadcrumb}\n\n"
        
        if len(chunks_in_section) > 1:
            chunk_index = chunks_in_section.index(doc) + 1
            total_chunks = len(chunks_in_section)
            structural_context += f"[Section split: Part {chunk_index} of {total_chunks}]\n\n"
        
        # Store original content (Clean Text requirement)
        doc.metadata["original_content"] = doc.page_content
        
        # Prepare for async enrichment
        if llm:
            tasks.append(_enrich_chunk(doc, global_summary, llm, semaphore))
        else:
            tasks.append(asyncio.sleep(0)) # Placeholder for no-LLM case
            
        processed_docs.append((doc, structural_context))

    # Run all enrichment tasks in parallel
    if llm and tasks:
        print(f"Enriching {len(tasks)} chunks in parallel (max 5 concurrent)...")
        enrichment_results = await asyncio.gather(*tasks)
    else:
        enrichment_results = [""] * len(processed_docs)

    final_docs = []
    for (doc, structural_context), enrichment in zip(processed_docs, enrichment_results):
        full_header = structural_context + enrichment
        if full_header:
            doc.page_content = f"{full_header}---CONTENT---\n\n{doc.page_content}"
        final_docs.append(doc)
            
    return final_docs

def _split_text(text):
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""] 
    )
    return char_splitter.create_documents([text])