import requests
import base64
import json
import os
from typing import List, Tuple

# Import the cleaner to process API results
try:
    from .cleaner import clean_text
except ImportError:
    from cleaner import clean_text

# --- Configuration ---
BASE_URL = "https://clueweb22.us/fineweb/search"

# --- Function ---

def retrieve_documents(query: str, api_key: str, top_k: int) -> List[Tuple[str, str]]:
    """
    Retrieve relevant documents for a given query using the FineWeb API.
    
    Args:
        query: User query to search for
        api_key: The FineWeb API key
        top_k: Number of top documents to retrieve
        
    Returns:
        List of tuples: (document_content, document_url)
    """
    
    if not api_key:
        print("Error: FineWeb API key is not set.")
        return []

    url = f"{BASE_URL}?query={query}&k={top_k}"
    headers = {"x-api-key": api_key}
    retrieved_docs = []

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            encoded_documents_list = data.get("results")

            if encoded_documents_list and isinstance(encoded_documents_list, list):
                for encoded_doc in encoded_documents_list:
                    try:
                        decoded_json_string = base64.b64decode(encoded_doc).decode('utf-8')
                        document = json.loads(decoded_json_string)
                        
                        # Extract content and URL
                        content = document.get("contents", document.get("text"))
                        url = document.get("url", "No URL provided")
                        
                        if content:
                            cleaned_content = clean_text(content)
                            retrieved_docs.append((cleaned_content, url))
                        else:
                            print(f"Warning: 'contents' or 'text' key not found in doc. Skipping.")
                            
                    except (TypeError, base64.binascii.Error, json.JSONDecodeError) as e:
                        print(f"Skipping a document due to a decoding/parsing error: {e}")
            else:
                print("API Warning: No results found or the format was not a list.")
        else:
            print(f"API Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network Error: Failed to connect to API. {e}")
        
    return retrieved_docs

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    TEST_API_KEY = os.environ.get("FINEWEB_API_KEY", "M8eTF0iASb08qLVCL0l2UyR5mFDmFQgj3am8ewVa1Yk")
    test_query = "what is machine learning"
    k = 3
    
    print(f"Testing retriever with query: '{test_query}' and k={k}")
    results = retrieve_documents(test_query, TEST_API_KEY, k)
    
    if results:
        print(f"\nSuccessfully retrieved {len(results)} documents.")
        for i, (doc, url) in enumerate(results):
            print(f"\n--- Document {i+1} from {url} ---")
            print(doc[:200] + "...")
    else:
        print("\nNo results retrieved.")