from sentence_transformers import SentenceTransformer
from api.config import Config

class EmbeddingService:
    """Handles text embedding generation"""
    
    _model = None  # Singleton pattern for model
    
    def __init__(self):
        if EmbeddingService._model is None:
            print(f"Loading embedding model: {Config.EMBEDDING_MODEL}...")
            EmbeddingService._model = SentenceTransformer(Config.EMBEDDING_MODEL)
            print("Embedding model loaded successfully!")
    
    def encode(self, text):
        """Convert text to embedding vector"""
        return EmbeddingService._model.encode(text, convert_to_numpy=True)
    
    def encode_batch(self, texts):
        """Convert multiple texts to embeddings"""
        return EmbeddingService._model.encode(texts, convert_to_numpy=True)