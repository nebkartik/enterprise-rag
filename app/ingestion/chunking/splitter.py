import logfire

def chunk_text(text: str, chunk_size:int=1500) -> list:
    
    if not text.strip():
        logfire.warning("⚠️ Received empty text for chunking.")
        return []
    
    text = text.strip()
    chunks = []
    current_chunk = ""

    paragraphs = text.split("\n\n")  # Split by paragraphs

    for p in paragraphs:
       if len(current_chunk) + len(p) < chunk_size:
           current_chunk += p + "\n\n"

       else:    
           if current_chunk.strip():
               chunks.append(current_chunk)
           current_chunk = p + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk)
    
    logfire.info(f"✅ Generated {len(chunks)} chunks from text of length {len(text)}")
    valid_chunks = [c for c in chunks if c.strip()]

    return valid_chunks


