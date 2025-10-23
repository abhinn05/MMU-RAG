import re
from typing import Optional

# To handle common text encoding issues and artifacts,
# it's highly recommended to install 'ftfy':
# pip install ftfy
try:
    import ftfy
except ImportError:
    print("Warning: 'ftfy' library not found. Advanced unicode fixing will be disabled.")
    print("Please install it with: pip install ftfy")
    ftfy = None

def clean_text(text: str) -> str:
    """
    Clean and preprocess raw text for better RAG performance.
    
    Args:
        text: Raw input text to be cleaned
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""

    # 1. Fix encoding issues and unicode artifacts (e.g., â€™ -> ’)
    if ftfy:
        text = ftfy.fix_text(text)

    # 2. Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # 3. Remove Markdown:
    # Remove links [text](url)
    text = re.sub(r'\[.*?\]\(.*?\)', ' ', text)
    # Remove bold, italics, code (`*`, `_`, '`')
    text = re.sub(r'([\*\_`])', ' ', text)
    # Remove headers
    text = re.sub(r'^\s*#+\s+', '', text, flags=re.MULTILINE)

    # 4. Convert to lowercase
    text = text.lower()

    # 5. Normalize whitespace:
    # Replace newlines, tabs, and carriage returns with a single space
    text = re.sub(r'[\n\t\r]', ' ', text)
    # Collapse multiple whitespace characters into a single space
    text = re.sub(r'\s+', ' ', text)

    # 6. Remove leading/trailing whitespace
    text = text.strip()
    
    return text

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    sample_text = """
    <p>This is a <b>test</b> document.</p>
    
    It includes:
    * Markdown lists
    * Extra     whitespace
    * And a [link](http://example.com)
    
    It also has some funny unicode like â€™s.
    
    # A Header
    And more text.
    """
    
    print("--- ORIGINAL TEXT ---")
    print(sample_text)
    
    cleaned = clean_text(sample_text)
    
    print("\n--- CLEANED TEXT ---")
    print(cleaned)

    # Expected output:
    # this is a test document. it includes: markdown lists extra whitespace and a link and a 's. a header and more text.