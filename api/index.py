from flask import Flask, request, jsonify, render_template
import os
from api.config import Config
from api.models import DocumentStore
from api.services import GeminiService

app = Flask(__name__, template_folder='templates')

# Initialize document store
doc_store = DocumentStore()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with semantic search"""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get API key from multiple sources
        api_key = (
            request.headers.get('X-API-Key') or 
            Config.GOOGLE_API_KEY or 
            data.get('api_key')
        )
        
        if not api_key:
            return jsonify({
                'error': 'API key required. Please enter your Google API key.'
            }), 401
        
        # Find relevant documents using semantic search
        relevant_docs = doc_store.find_relevant_docs(
            question, 
            top_k=Config.TOP_K_DOCUMENTS,
            threshold=Config.SIMILARITY_THRESHOLD
        )
        
        # Build prompt and get response
        prompt = GeminiService.build_prompt_with_context(question, relevant_docs)
        answer = GeminiService.generate_response(prompt, api_key)
        
        return jsonify({
            'answer': answer,
            'sources': [name for name, _, _ in relevant_docs],
            'similarities': [float(score) for _, _, score in relevant_docs]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({
                'error': f'Only {", ".join(Config.ALLOWED_EXTENSIONS)} files are supported'
            }), 400
        
        # Read and add document
        content = file.read().decode('utf-8')
        doc_store.add_document(file.filename, content)
        
        return jsonify({
            'message': f'Document "{file.filename}" uploaded and embedded successfully!',
            'total_docs': doc_store.get_document_count()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all loaded documents"""
    return jsonify({
        'documents': doc_store.get_all_documents(),
        'count': doc_store.get_document_count()
    })

@app.route('/api/documents/<doc_name>', methods=['DELETE'])
def delete_document(doc_name):
    """Delete a specific document"""
    if doc_store.remove_document(doc_name):
        return jsonify({
            'message': f'Document "{doc_name}" deleted successfully',
            'remaining': doc_store.get_document_count()
        })
    return jsonify({'error': 'Document not found'}), 404

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(Config.GOOGLE_API_KEY),
        'documents_loaded': doc_store.get_document_count(),
        'embedding_model': Config.EMBEDDING_MODEL,
        'semantic_search': 'enabled',
        'config': {
            'top_k': Config.TOP_K_DOCUMENTS,
            'similarity_threshold': Config.SIMILARITY_THRESHOLD
        }
    })

# Required for Vercel
app = app