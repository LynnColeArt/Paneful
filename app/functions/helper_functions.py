import hashlib

def calculate_md5(image_data):
    """Calculate the MD5 hash of image data."""
    hasher = hashlib.md5()
    if isinstance(image_data, bytes):
        hasher.update(image_data)
    else:
        hasher.update(str(image_data).encode('utf-8'))
    return hasher.hexdigest()

def load_words(dictionary_path='meaningless-words/dictionary.txt'):
    """Load and properly split words from the dictionary file.
    
    Args:
        dictionary_path (str): Path to the dictionary file
        
    Returns:
        list: List of individual words
    """
    try:
        with open(dictionary_path, 'r') as file:
            # Split the content by whitespace and filter out empty strings
            words = [word.strip() for word in file.read().split() if word.strip()]
        if not words:
            print("No words found in dictionary")
            return ["DADA"]  # Fallback word
        print(f"Loaded {len(words)} words from dictionary")  # Debug info
        return words
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return ["DADA"]  # Fallback word
