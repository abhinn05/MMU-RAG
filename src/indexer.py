import os
import json
from typing import List

# This script requires FAISS and sentence-transformers:
# pip install faiss-gpu sentence-transformers
# (or pip install faiss-gpu if you have a CUDA-enabled GPU)
try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Warning: 'faiss-cpu' or 'sentence-transformers' not found.")
    print("Please install them with: pip install faiss-cpu sentence-transformers")
    faiss = None
    SentenceTransformer = None

# --- Configuration ---

# We MUST use the same model that was used in tokenizer.py
# to ensure consistency between token counting and embedding.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

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

def build_index(chunks: List[str], index_path: str):
    """
    Build and save a FAISS index from document chunks.
    
    Saves two files:
    1. index_path + ".faiss" (the vector index)
    2. index_path + ".chunks.json" (the mapping from ID to text)
    
    Args:
        chunks: List of text chunks to index
        index_path: The *base path* where the index and chunk files
                    should be saved (e.g., "my_index")
    """
    if not model or not faiss:
        print("Error: Required libraries (FAISS, SentenceTransformers) not loaded.")
        return

    if not chunks:
        print("Warning: No chunks provided to build_index. Aborting.")
        return

    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    # 1. Generate embeddings for each chunk
    # show_progress_bar=True is helpful for large datasets
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    # Get the dimensionality of the embeddings
    d = embeddings.shape[1]
    
    # 2. Create FAISS index
    # We use IndexFlatL2 for exact, brute-force search.
    # It's good for starters and smaller datasets.
    # For larger datasets, one might use IndexIVFFlat.
    index = faiss.IndexFlatL2(d)
    
    # 3. Add embeddings to the index
    print("Adding embeddings to FAISS index...")
    index.add(embeddings)
    
    # 4. Save the index and the chunk data
    faiss_file = f"{index_path}.faiss"
    chunks_file = f"{index_path}.chunks.json"
    
    try:
        # Save FAISS index to disk
        print(f"Saving FAISS index to: {faiss_file}")
        faiss.write_index(index, faiss_file)
        
        # Save the chunks themselves for retrieval
        # We store them as a dictionary: {index: text}
        print(f"Saving chunk text data to: {chunks_file}")
        chunk_data = {i: chunk for i, chunk in enumerate(chunks)}
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
            
        print("Indexing complete.")

    except Exception as e:
        print(f"Error saving index or chunk data: {e}")

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    if model and faiss:
        test_chunks = [
            "Machine learning is a subfield of artificial intelligence.",
            "It focuses on the development of algorithms.",
            "These algorithms enable computers to learn from and make predictions.",
            "Deep learning is a subset of machine learning based on neural networks."
        ]
        
        test_index_path = "test_index"
        
        print(f"\n--- Building test index at '{test_index_path}' ---")
        build_index(test_chunks, test_index_path)
        
        # Check if files were created
        faiss_created = os.path.exists(f"{test_index_path}.faiss")
        chunks_created = os.path.exists(f"{test_index_path}.chunks.json")
        
        print(f"\nIndex file created: {faiss_created}")
        print(f"Chunks file created: {chunks_created}")
        
        # Clean up
        if faiss_created:
            os.remove(f"{test_index_path}.faiss")
        if chunks_created:
            os.remove(f"{test_index_path}.chunks.json")
            
        print("Cleanup complete.")
    else:
        print("\nSkipping test: libraries not loaded.")