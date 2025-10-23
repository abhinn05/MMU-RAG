import os
import yaml
from typing import Dict, Any, List

# This script requires PyYAML: pip install PyYAML
try:
    import yaml
except ImportError:
    print("Warning: 'PyYAML' library not found. Config loading will fail.")
    print("Please install it with: pip install PyYAML")
    yaml = None

# Import all components for the new pipeline
try:
    from .retriever import retrieve_documents
    from .re_ranker import rerank_chunks
    from .generator import generate_answer
except ImportError:
    from retriever import retrieve_documents
    from re_ranker import rerank_chunks
    from generator import generate_answer

# --- Configuration Cache ---
config_cache: Dict[str, Any] = {}

def load_config(config_path: str) -> Dict[str, Any]:
    """Loads configuration from a YAML file, with caching."""
    if config_path in config_cache:
        return config_cache[config_path]
    
    if not yaml:
        raise ImportError("PyYAML is not installed. Cannot load config.")
        
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not config:
                raise ValueError("Config file is empty or invalid.")
            config_cache[config_path] = config
            return config
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        raise

def run_rag(query: str, config_path: str) -> str:
    """
    Execute the complete 2-stage RAG pipeline for a given query.
    
    Args:
        query: User query to process
        config_path: Path to configuration YAML file
        
    Returns:
        Generated answer from the RAG system
    """
    try:
        # 1. Load configuration
        config = load_config(config_path)
        
        # Get API key from config OR environment variable
        api_key = os.environ.get("FINEWEB_API_KEY", config.get('fineweb_api_key'))
        retriever_top_k = config.get('retriever_top_k', 5)
        generator_model = config.get('generator_model')
        chunk_size = config.get('chunk_size', 256)
        chunk_overlap = config.get('chunk_overlap', 50)
        rerank_top_k = config.get('rerank_top_k', 3)
        
        if not api_key:
            raise ValueError("FINEWEB_API_KEY not found in config or environment variables.")
        if not generator_model:
            raise ValueError("Config missing 'generator_model'.")

        # 2. Stage 1: Retrieve relevant documents
        print(f"Stage 1: Retrieving top-{retriever_top_k} documents from FineWeb...")
        documents_with_urls = retrieve_documents(query, api_key, retriever_top_k)
        
        if not documents_with_urls:
            print("No documents found from FineWeb.")
            return "I could not find any relevant information to answer your question."
        
        document_texts = [doc for doc, url in documents_with_urls]

        # 3. Stage 2: Re-Rank chunks from retrieved documents
        print(f"Stage 2: Processing {len(document_texts)} docs and re-ranking for top-{rerank_top_k} chunks...")
        final_contexts = rerank_chunks(
            query=query,
            documents=document_texts,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=rerank_top_k
        )
        
        if not final_contexts:
            print("No relevant chunks found after re-ranking.")
            return "I found some documents, but no specific information to answer your question."

        # 4. Generate answer
        print(f"Stage 3: Generating answer using model: {generator_model}...")
        answer = generate_answer(query, final_contexts, generator_model)
        
        # 5. Return final answer
        return answer

    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        return f"An error occurred while processing your request: {e}"