from typing import List

# This script requires the 'transformers' and 'sentence-transformers' libraries:
# pip install transformers sentence-transformers
try:
    from transformers import AutoTokenizer
except ImportError:
    print("Warning: 'transformers' library not found. Tokenization will not work.")
    print("Please install it with: pip install transformers sentence-transformers")
    AutoTokenizer = None

# --- Configuration ---
# We use a model popular for sentence embeddings and retrieval tasks.
TOKENIZER_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize the tokenizer once when the module is loaded.
if AutoTokenizer:
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
        print(f"Successfully loaded tokenizer: {TOKENIZER_NAME}")
    except Exception as e:
        print(f"Error loading tokenizer {TOKENIZER_NAME}: {e}")
        tokenizer = None
else:
    tokenizer = None

# --- Function ---

def tokenize(text: str) -> List[int]:
    """
    Tokenize text using HuggingFace AutoTokenizer.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of token IDs
    """
    if not tokenizer:
        print("Error: Tokenizer is not loaded. Returning empty list.")
        return []
        
    if not text:
        return []

    try:
        encoding = tokenizer(
            text, 
            add_special_tokens=False, 
            truncation=False,
            return_attention_mask=False
        )
        return encoding['input_ids']
        
    except Exception as e:
        print(f"Error during tokenization: {e}")
        return []

def detokenize(token_ids: List[int]) -> str:
    """
    Convert a list of token IDs back into a string.
    """
    if not tokenizer:
        print("Error: Tokenizer is not loaded. Cannot detokenize.")
        return ""
    
    return tokenizer.decode(token_ids, skip_special_tokens=True)

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    if tokenizer:
        sample_text = "This is a simple sentence for tokenization."
        print(f"\n--- ORIGINAL TEXT ---")
        print(sample_text)
        
        token_ids = tokenize(sample_text)
        print(f"\n--- TOKEN IDS ---")
        print(token_ids)
        
        decoded_text = detokenize(token_ids)
        print(f"\n--- DECODED TEXT ---")
        print(decoded_text)
    else:
        print("\nTokenizer not loaded. Cannot run test.")