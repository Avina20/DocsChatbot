import numpy as np
from embeddings.services.embedding_service import EmbeddingService

class DocumentStore:
    """Manages documents and their embeddings"""
    
    def __init__(self):
        self.documents = {}
        self.embeddings = {}
        self.embedding_service = EmbeddingService()
        self._initialize_sample_documents()
        
    def _initialize_sample_documents(self):
        """Load sample documents"""
        samples = {
            'python_intro.txt': (
                'Python is a high-level programming language known for its '
                'simplicity and readability. It was created by Guido van Rossum '
                'and first released in 1991. Python supports multiple programming '
                'paradigms including procedural, object-oriented, and functional programming.'
            ),
            'langchain_info.txt': (
                'LangChain is a framework for developing applications powered by '
                'language models. It provides tools for chaining together different '
                'components to build complex AI applications. LangChain supports '
                'various LLMs and provides abstractions for common tasks.'
            ),
            'gemini_info.txt': (
                'Gemini 2.0 Flash is Google\'s latest AI model, optimized for '
                'speed and efficiency while maintaining high quality responses. '
                'It excels at reasoning, coding, and multimodal understanding. '
                'The model supports both text and image inputs.'
            )
        }
        
        for name, content in samples.items():
            self.add_document(name, content)
    
    def add_document(self, name, content):
        """Add document and compute its embedding"""
        self.documents[name] = content
        embedding = self.embedding_service.encode(content)
        self.embeddings[name] = embedding
        
    def remove_document(self, name):
        """Remove a document"""
        if name in self.documents:
            del self.documents[name]
            del self.embeddings[name]
            return True
        return False
        
    def find_relevant_docs(self, question, top_k=3, threshold=0.2):
        """Find most relevant documents using semantic similarity"""
        if not self.documents:
            return []
        
        # Generate embedding for the question
        question_embedding = self.embedding_service.encode(question)
        
        # Calculate cosine similarity with all documents
        similarities = []
        for doc_name, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(question_embedding, doc_embedding)
            similarities.append((doc_name, self.documents[doc_name], similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # Return top_k most relevant documents above threshold
        return [
            (name, content, score) 
            for name, content, score in similarities[:top_k] 
            if score > threshold
        ]
    
    @staticmethod
    def _cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (
            np.linalg.norm(vec1) * np.linalg.norm(vec2)
        )
    
    def get_all_documents(self):
        """Get list of all document names"""
        return list(self.documents.keys())
    
    def get_document_count(self):
        """Get total number of documents"""
        return len(self.documents)
    
    def get_document_content(self, name):
        """Get content of a specific document"""
        return self.documents.get(name)