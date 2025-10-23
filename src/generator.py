from typing import List, Dict

# This script requires 'transformers' and 'torch'
# pip install transformers torch
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
except ImportError:
    print("Warning: 'transformers' or 'torch' not found.")
    print("Please install with: pip install transformers torch")
    pipeline = None
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None

# --- Caching ---
# We cache the loaded models/pipelines in memory to avoid reloading
# on every API request. The key will be the model_name.
generator_cache: Dict[str, "pipeline"] = {}

# --- Function ---

def _build_prompt(query: str, contexts: List[str]) -> str:
    """
    Creates a prompt for the model, combining the query and contexts.
    
    This format is designed for text2text-generation models
    like FLAN-T5.
    """
    # Join all context chunks into a single string
    context_str = "\n\n".join(contexts)
    
    # Create the prompt
    prompt = f"""Answer the following question based only on the context provided.

    Context:
    {context_str}

    Question:
    {query}

    Answer in 3-5 sentences with relevant details:
    """
    return prompt

def generate_answer(question, contexts, model_name="google/flan-t5-base"):
    try:
        print(f"Loading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Combine and trim context (prevent token overflow)
        context_text = " ".join(contexts)
        if len(context_text.split()) > 400:
            context_text = " ".join(context_text.split()[:400])

        prompt = f"""You are an expert AI assistant.
Use the following context to answer the question clearly and concisely.

Context:
{context_text}

Question:
{question}

Answer in 3–5 sentences:"""

        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

        # Generate with sampling for richer output
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            top_p=0.9,
            temperature=0.8
        )

        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Generated answer:", answer)
        return answer

    except Exception as e:
        print(f"Error loading or generating with model {model_name}: {e}")
        return f"Error: Could not load model {model_name}." 
# --- Example Usage (for testing) ---
if __name__ == "__main__":
    if pipeline:
        # Use a small, fast model for testing
        test_model = "google/flan-t5-small"
        
        test_query = "What is deep learning?"
        
        test_contexts = [
            "Machine learning is a subfield of artificial intelligence.",
            "It focuses on the development of algorithms.",
            "These algorithms enable computers to learn from and make predictions.",
            "Deep learning is a subset of machine learning based on neural networks."
        ]
        
        print(f"\n--- Generating answer for: '{test_query}' ---")
        print(f"--- Using model: '{test_model}' ---")
        
        answer = generate_answer(test_query, test_contexts, test_model)
        
        print("\n--- Generated Answer ---")
        print(answer)
        
        # Expected: "a subset of machine learning based on neural networks" or similar.
        assert "neural networks" in answer or "subset of machine learning" in answer

        # Test cache
        print("\n--- Testing cache (should not reload model) ---")
        answer_cached = generate_answer(test_query, test_contexts, test_model)
        assert answer == answer_cached
        print("Cached generation successful.")
        
    else:
        print("\nSkipping test: libraries not loaded.")