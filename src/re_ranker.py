from typing import List

# This script requires FAISS and sentence-transformers
try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Warning: 'faiss-cpu' or 'sentence-transformers' not found.")
    print("Please install them with: pip install faiss-cpu sentence-transformers")
    faiss = None
    SentenceTransformer = None

# Import our project's tokenizer and chunker
try:
    from .tokenizer import tokenize, detokenize, TOKENIZER_NAME
    from .chunker import chunk_tokens
except ImportError:
    from tokenizer import tokenize, detokenize, TOKENIZER_NAME
    from chunker import chunk_tokens

# --- Configuration ---
# We MUST use the same model from the tokenizer for embedding
MODEL_NAME = TOKENIZER_NAME

# Initialize the model once
if SentenceTransformer:
    try:
        model = SentenceTransformer(MODEL_NAME)
        print(f"Successfully loaded embedding model: {MODEL_NAME}")
    except Exception as e:
        print(f"Error loading embedding model {MODEL_NAME}: {e}")
        model = None
else:
    model = None

# --- Function ---

def rerank_chunks(query: str, documents: List[str], chunk_size: int, chunk_overlap: int, top_k: int) -> List[str]:
    """
    Takes a query and a list of large documents, processes them into
    chunks, and returns the top_k most relevant chunks.
    
    Args:
        query: The user's original query.
        documents: A list of large document texts.
        chunk_size: The target size for each chunk.
        chunk_overlap: The overlap between chunks.
        top_k: The number of chunks to return.
        
    Returns:
        A list of the top_k most relevant text chunks.
    """
    if not model or not faiss:
        print("Error: re_ranker dependencies (FAISS, SentenceTransformers) not loaded.")
        return []
    
    # 1. Process all documents into a single list of text chunks
    all_text_chunks = []
    for doc in documents:
        # 1a. Tokenize
        tokens = tokenize(doc)
        if not tokens:
            continue
        
        # 1b. Chunk
        token_chunks = chunk_tokens(tokens, chunk_size, chunk_overlap)
        
        # 1c. Detokenize back to text
        for chunk in token_chunks:
            all_text_chunks.append(detokenize(chunk))
    
    if not all_text_chunks:
        print("No chunks were generated from the retrieved documents.")
        return []
    
    print(f"Created {len(all_text_chunks)} chunks from {len(documents)} documents.")
    
    # 2. Generate embeddings for all chunks
    try:
        chunk_embeddings = model.encode(all_text_chunks, show_progress_bar=False)
        d = chunk_embeddings.shape[1]
    except Exception as e:
        print(f"Error encoding chunks: {e}")
        return []
    
    # 3. Build a temporary, in-memory FAISS index
    index = faiss.IndexFlatL2(d)
    index.add(chunk_embeddings)
    
    # 4. Generate query embedding
    try:
        query_embedding = model.encode([query])
    except Exception as e:
        print(f"Error encoding query: {e}")
        return []
    
    # 5. Search the index
    # D = distances, I = indices (IDs)
    try:
        D, I = index.search(query_embedding, top_k)
        retrieved_ids = I[0]
    except Exception as e:
        print(f"Error searching in-memory index: {e}")
        return []
    
    # 6. Map IDs back to text chunks
    final_chunks = [all_text_chunks[idx] for idx in retrieved_ids if idx >= 0]
    
    return final_chunks

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    if model and faiss:
        test_query = "What is deep learning?"
        
        test_documents = [
            "Machine learning is a subfield of artificial intelligence. It focuses on algorithms.",
            "Deep learning is a subset of machine learning based on neural networks. It has many layers.",
            "RAG stands for Retrieval-Augmented Generation. It uses a retriever and a generator."
        ]
        
        print(f"\n--- Re-ranking {len(test_documents)} docs for query: '{test_query}' ---")
        
        chunks = rerank_chunks(
            query=test_query,
            documents=test_documents,
            chunk_size=15,    # Small chunk size for testing
            chunk_overlap=5,
            top_k=2
        )
        
        print("\n--- Top 2 Chunks Found ---")
        for i, chunk in enumerate(chunks):
            print(f"{i+1}: {chunk}")
            
        assert len(chunks) == 2
        assert "deep learning" in chunks[0].lower()
    else:
        print("\nSkipping test: libraries not loaded.")