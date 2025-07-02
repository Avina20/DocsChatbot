# DocsChatbot
Conversational AI system implementing Retrieval-Augmented Generation (RAG) architecture using Google's Gemini 2.0 Flash LLM with custom LangChain integration

The system leverages FAISS vector similarity search over HuggingFace sentence-transformers embeddings for semantic document retrieval, coupled with conversational memory buffer management for context-aware multi-turn dialogues. Built with a custom Pydantic-validated LLM wrapper that interfaces directly with Google's Generative Language API v1beta endpoints, featuring recursive character-based text chunking and ConversationalRetrievalChain orchestration for production-scale document query processing.

## Technologies

- LLM Backend: Google Gemini 2.0 Flash via REST API (generativelanguage.googleapis.com/v1beta)
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional dense vectors)
- Vector Store: Facebook AI Similarity Search (FAISS) with L2 distance indexing
- Framework: LangChain with custom Pydantic LLM wrapper extending langchain.llms.base.LLM
- Text Processing: RecursiveCharacterTextSplitter (1000 char chunks, 200 overlap)
- Memory Management: ConversationBufferMemory with return_messages=True
- Retrieval Strategy: Top-k=3 similarity search with source document attribution


