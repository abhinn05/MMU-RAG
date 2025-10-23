from typing import List

def chunk_tokens(tokens: List[int], size: int, overlap: int) -> List[List[int]]:
    """
    Split token sequences into overlapping chunks for processing.
    
    Args:
        tokens: List of token IDs to chunk
        size: Maximum size of each chunk
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        List of token chunks (each chunk is a list of token IDs)
    """
    
    if not tokens:
        return []

    if overlap >= size:
        raise ValueError("Overlap size must be smaller than chunk size.")

    step = size - overlap
    
    if len(tokens) <= size:
        return [tokens]

    chunks = []
    
    for i in range(0, len(tokens), step):
        chunk = tokens[i : i + size]
        
        if chunk:
            # We break if the last chunk is just the overlap from the previous one
            if len(chunk) < overlap and i > 0:
                break
            chunks.append(chunk)

    return chunks

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    sample_tokens = list(range(25))
    chunk_size = 10
    overlap_size = 2
    
    print(f"--- ORIGINAL TOKENS (length {len(sample_tokens)}) ---")
    print(sample_tokens)
    
    chunks = chunk_tokens(sample_tokens, chunk_size, overlap_size)
    
    print(f"\n--- CHUNKS (size={chunk_size}, overlap={overlap_size}) ---")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i} (length {len(chunk)}): {chunk}")