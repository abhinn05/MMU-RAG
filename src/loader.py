import os
import json
from typing import List, Tuple, Optional

# To handle PDFs, you'll need to install pypdf:
# pip install pypdf
try:
    from pypdf import PdfReader
except ImportError:
    print("Warning: 'pypdf' library not found. PDF loading will be disabled.")
    print("Please install it with: pip install pypdf")
    PdfReader = None

def _load_file(file_path: str) -> Optional[str]:
    """Helper function to load content from a single file."""
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            if PdfReader is None:
                print(f"Skipping PDF {file_path}, 'pypdf' is not installed.")
                return None
            
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            return "\n\n".join(text_parts)

        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Try to find a 'text' or 'content' key,
                # otherwise, just serialize the whole JSON object as text.
                if isinstance(data, dict):
                    if 'text' in data:
                        return str(data['text'])
                    if 'content' in data:
                        return str(data['content'])
                return json.dumps(data, indent=2)
        
        elif ext == '.jsonl':
            text_parts = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if isinstance(data, dict):
                            if 'text' in data:
                                text_parts.append(str(data['text']))
                            elif 'content' in data:
                                text_parts.append(str(data['content']))
                            else:
                                # Fallback for unknown JSONL structure
                                text_parts.append(json.dumps(data))
                        else:
                            text_parts.append(str(data))
            return "\n\n".join(text_parts)

        else:
            print(f"Skipping unsupported file type: {file_path}")
            return None

    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def load_corpus(path: str) -> List[Tuple[str, str]]:
    """
    Load documents from the specified path.
    
    Args:
        path: Path to the document corpus directory or file
        
    Returns:
        List of tuples containing (document_id, document_text)
    """
    documents = []
    
    if not os.path.exists(path):
        print(f"Error: Path not found: {path}")
        return documents

    if os.path.isdir(path):
        print(f"Loading documents from directory: {path}")
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                content = _load_file(file_path)
                if content:
                    documents.append((file_path, content))
                    
    elif os.path.isfile(path):
        print(f"Loading document from file: {path}")
        content = _load_file(path)
        if content:
            documents.append((path, content))
            
    else:
        print(f"Error: Path is not a valid file or directory: {path}")

    print(f"Successfully loaded {len(documents)} document(s).")
    return documents

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # To test this, create a dummy 'data' directory with some files
    # e.g., data/sample.txt, data/report.pdf, data/info.json
    
    # Create dummy files for testing
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open("data/sample.txt", "w") as f:
        f.write("This is a sample text file for the loader.")
        
    with open("data/info.json", "w") as f:
        json.dump({"id": 1, "content": "This is content from a JSON file."}, f)
        
    with open("data/logs.jsonl", "w") as f:
        f.write('{"timestamp": "2025-01-01", "text": "First log entry."}\n')
        f.write('{"timestamp": "2025-01-02", "text": "Second log entry."}\n')

    print("--- Testing with directory 'data/' ---")
    docs = load_corpus("data")
    for doc_id, text in docs:
        print(f"\n[Doc ID: {doc_id}]")
        print(text[:100] + "...") # Print first 100 chars

    print("\n--- Testing with single file 'data/sample.txt' ---")
    docs_single = load_corpus("data/sample.txt")
    if docs_single:
        print(f"[Doc ID: {docs_single[0][0]}]")
        print(docs_single[0][1])
        
    # Clean up dummy files
    import shutil
    shutil.rmtree("data")