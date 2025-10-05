import os

class Config:
    """Application configuration"""
    
    # Google API settings
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    # Embedding model settings
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # Search settings
    TOP_K_DOCUMENTS = 3
    SIMILARITY_THRESHOLD = 0.2
    
    # Gemini API settings
    GEMINI_MODEL = 'gemini-2.0-flash'
    GEMINI_TEMPERATURE = 0.7
    GEMINI_MAX_TOKENS = 1000
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB