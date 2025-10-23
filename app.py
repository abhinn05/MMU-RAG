import uvicorn
import asyncio
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

# Import the RAG components directly
try:
    from src.pipeline import run_rag, load_config
    from src.retriever import retrieve_documents
    from src.re_ranker import rerank_chunks
    from src.generator import generate_answer
except ImportError:
    print("Could not import from 'src', trying relative import...")
    try:
        from pipeline import run_rag, load_config
        from retriever import retrieve_documents
        from re_ranker import rerank_chunks
        from generator import generate_answer
    except ImportError:
        print("Fatal: Could not find 'pipeline.py', 'retriever.py', 're_ranker.py' or 'generator.py'.")
        exit(1)


# --- Configuration ---
CONFIG_PATH = "config.yaml"

# --- Pydantic Models ---
class HealthResponse(BaseModel): status: str = "ok"
class RunRequest(BaseModel): question: str
class EvaluateRequest(BaseModel): query: str; iid: str
class EvaluateResponse(BaseModel): query_id: str; generated_response: str
class StreamResponse(BaseModel):
    intermediate_steps: Optional[str] = None
    final_report: Optional[str] = None
    is_intermediate: bool
    citations: List[str] = []
    complete: bool
    error: Optional[str] = None

# --- FastAPI App ---
app = FastAPI(
    title="RAG System API",
    description="API for the MMU-RAGent competition-compliant RAG system."
)

# --- Endpoint 1: /health ---
@app.get("/health", response_model=HealthResponse)
async def get_health():
    return HealthResponse(status="ok")

# --- Endpoint 2: /run (Dynamic Evaluation) ---
async def stream_rag_response(question: str):
    """
    A generator function that yields Server-Sent Events (SSE)
    for the /run endpoint, with detailed intermediate steps.
    """
    loop = asyncio.get_event_loop()
    contexts = []
    
    try:
        # Step 1: Send "thinking" status
        yield "data: " + StreamResponse(
            intermediate_steps="Query received. Initializing RAG pipeline...",
            final_report=None,
            is_intermediate=True,
            complete=False
        ).model_dump_json() + "\n\n"
        
        # Step 2: Load configuration
        config = await loop.run_in_executor(None, load_config, CONFIG_PATH)
        
        api_key = os.environ.get("FINEWEB_API_KEY", config.get('fineweb_api_key'))
        retriever_top_k = config.get('retriever_top_k', 5)
        generator_model = config.get('generator_model')
        chunk_size = config.get('chunk_size', 256)
        chunk_overlap = config.get('chunk_overlap', 50)
        rerank_top_k = config.get('rerank_top_k', 3)

        if not api_key or not generator_model:
            raise ValueError("Config is missing 'fineweb_api_key' or 'generator_model'")

        yield "data: " + StreamResponse(
            intermediate_steps="Stage 1: Configuration loaded. Retrieving documents from FineWeb API...",
            final_report=None,
            is_intermediate=True,
            complete=False
        ).model_dump_json() + "\n\n"

        # Step 3: Run Stage 1 Retrieval (in a thread)
        documents_with_urls = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            retrieve_documents,
            question,
            api_key,
            retriever_top_k
        )
        
        if not documents_with_urls:
            yield "data: " + StreamResponse(
                intermediate_steps="Stage 1: No documents found on FineWeb for this query.",
                final_report="I could not find any relevant information to answer your question.",
                is_intermediate=False,
                complete=True
            ).model_dump_json() + "\n\n"
            return

        document_texts = [doc for doc, url in documents_with_urls]
        citations = [url for doc, url in documents_with_urls] # Capture citations

        # Step 4: Send "processing" status
        intermediate_message = f"Stage 1: Retrieved {len(document_texts)} documents.|||---|||Stage 2: Processing and re-ranking chunks..."
        yield "data: " + StreamResponse(
            intermediate_steps=intermediate_message,
            final_report=None,
            is_intermediate=True,
            complete=False,
            citations=citations # Show citations early
        ).model_dump_json() + "\n\n"

        # Step 5: Run Stage 2 Re-ranking (in a thread)
        final_contexts = await loop.run_in_executor(
            None,
            rerank_chunks,
            question,
            document_texts,
            chunk_size,
            chunk_overlap,
            rerank_top_k
        )
        
        if not final_contexts:
            yield "data: " + StreamResponse(
                intermediate_steps="Stage 2: No relevant chunks found after re-ranking.",
                final_report="I found documents, but no specific information to answer your question.",
                is_intermediate=False,
                complete=True,
                citations=citations
            ).model_dump_json() + "\n\n"
            return

        # Step 6: Send "generating" status
        intermediate_message = f"Stage 2: Found {len(final_contexts)} relevant chunks.|||---|||Stage 3: Generating final answer..."
        yield "data: " + StreamResponse(
            intermediate_steps=intermediate_message,
            final_report=None,
            is_intermediate=True,
            complete=False,
            citations=citations
        ).model_dump_json() + "\n\n"
        
        # Step 7: Run Stage 3 Generation (in a thread)
        answer = await loop.run_in_executor(
            None,
            generate_answer,
            question,
            final_contexts,
            generator_model
        )

        # Step 8: Send the final answer
        yield "data: " + StreamResponse(
            intermediate_steps=intermediate_message, # Keep last step
            final_report=answer,
            is_intermediate=False,
            citations=citations,
            complete=False # Not complete until the next message
        ).model_dump_json() + "\n\n"
        
        # Step 9: Send the completion signal
        yield "data: " + StreamResponse(
            intermediate_steps=intermediate_message,
            final_report=answer,
            is_intermediate=False,
            citations=citations,
            complete=True
        ).model_dump_json() + "\n\n"

    except Exception as e:
        print(f"Error in /run stream: {e}")
        error_message = f"An error occurred: {e}"
        yield "data: " + StreamResponse(
            error=error_message,
            is_intermediate=False,
            complete=True
        ).model_dump_json() + "\n\n"

@app.post("/run")
async def run_endpoint(request: RunRequest):
    return StreamingResponse(
        stream_rag_response(request.question),
        media_type="text/event-stream"
    )

# --- Endpoint 3: /evaluate (Static Evaluation) ---
@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_endpoint(request: EvaluateRequest):
    """
    Handles static evaluation.
    This calls the all-in-one 'run_rag' function.
    """
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            run_rag,
            request.query,
            CONFIG_PATH
        )
        
        response_data = EvaluateResponse(
            query_id=request.iid,
            generated_response=answer
        )
        
        try:
            with open("result.jsonl", "a", encoding="utf-8") as f:
                f.write(response_data.model_dump_json() + "\n")
        except Exception as e:
            print(f"Warning: Failed to write to result.jsonl: {e}")

        return response_data

    except Exception as e:
        print(f"Error in /evaluate endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {e}"}
        )

# --- Main execution ---
if __name__ == "__main__":
    if os.path.exists("result.jsonl"):
        os.remove("result.jsonl")
        print("Removed old 'result.jsonl' file.")

    print(f"Starting RAG server at http://localhost:5010")
    print("Ensure 'config.yaml' is present.")
    uvicorn.run(app, host="0.0.0.0", port=5010)