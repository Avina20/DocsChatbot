from flask import Flask, request, jsonify, render_template_string
import requests
import os
from functools import lru_cache

app = Flask(__name__)

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Chatbot</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
            <!-- Header -->
            <div class="bg-indigo-600 text-white p-6">
                <h1 class="text-2xl font-bold mb-2">🤖 Document Chatbot</h1>
                <p class="text-indigo-100">Ask questions about Python, LangChain, or Gemini</p>
            </div>

            <!-- Messages Container -->
            <div id="messages" class="p-6 space-y-4 h-96 overflow-y-auto bg-gray-50">
                <div class="text-center text-gray-500 py-8">
                    <p class="mb-2">👋 Welcome! Start asking questions.</p>
                    <p class="text-sm">Sample documents are already loaded.</p>
                </div>
            </div>

            <!-- Input Form -->
            <div class="p-6 bg-white border-t border-gray-200">
                <div class="flex gap-3">
                    <input 
                        type="text" 
                        id="userInput" 
                        placeholder="Ask a question..." 
                        class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        onkeypress="handleKeyPress(event)"
                    />
                    <button 
                        onclick="sendMessage()" 
                        id="sendBtn"
                        class="bg-indigo-600 text-white px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors font-medium"
                    >
                        Send
                    </button>
                </div>
                <div class="mt-3 flex gap-2">
                    <button 
                        onclick="clearChat()" 
                        class="text-sm text-gray-600 hover:text-gray-900"
                    >
                        🗑️ Clear Chat
                    </button>
                    <button 
                        onclick="uploadDocument()" 
                        class="text-sm text-indigo-600 hover:text-indigo-800"
                    >
                        📄 Upload Document
                    </button>
                </div>
                <input type="file" id="fileInput" accept=".txt" style="display: none;" onchange="handleFileUpload(event)" />
            </div>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(content, type) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'}`;
            
            const bubble = document.createElement('div');
            bubble.className = `max-w-[80%] rounded-2xl px-4 py-3 ${
                type === 'user' 
                    ? 'bg-indigo-600 text-white' 
                    : type === 'error'
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-white shadow-md text-gray-900'
            }`;
            bubble.innerHTML = content;
            
            msgDiv.appendChild(bubble);
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function addLoadingMessage() {
            const msgDiv = document.createElement('div');
            msgDiv.id = 'loading';
            msgDiv.className = 'flex justify-start';
            msgDiv.innerHTML = `
                <div class="bg-white shadow-md rounded-2xl px-4 py-3">
                    <span class="text-gray-600">🤔 Thinking...</span>
                </div>
            `;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function removeLoadingMessage() {
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
        }

        async function sendMessage() {
            const question = userInput.value.trim();
            if (!question) return;

            addMessage(question, 'user');
            userInput.value = '';
            sendBtn.disabled = true;
            addLoadingMessage();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });

                const data = await response.json();
                removeLoadingMessage();

                if (data.error) {
                    addMessage(`❌ Error: ${data.error}`, 'error');
                } else {
                    let answer = data.answer;
                    if (data.sources && data.sources.length > 0) {
                        answer += `<div class="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                            📚 Sources: ${data.sources.join(', ')}
                        </div>`;
                    }
                    addMessage(answer, 'assistant');
                }
            } catch (error) {
                removeLoadingMessage();
                addMessage(`❌ Error: ${error.message}`, 'error');
            } finally {
                sendBtn.disabled = false;
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function clearChat() {
            messagesDiv.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <p>Chat cleared! Start a new conversation.</p>
                </div>
            `;
        }

        function uploadDocument() {
            document.getElementById('fileInput').click();
        }

        async function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            addLoadingMessage();

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                removeLoadingMessage();

                if (data.error) {
                    addMessage(`❌ ${data.error}`, 'error');
                } else {
                    addMessage(`✅ ${data.message}`, 'system');
                }
            } catch (error) {
                removeLoadingMessage();
                addMessage(`❌ Upload failed: ${error.message}`, 'error');
            }

            event.target.value = '';
        }
    </script>
</body>
</html>
'''

# Sample documents (in-memory storage)
documents = {
    'python_intro.txt': 'Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.',
    'langchain_info.txt': 'LangChain is a framework for developing applications powered by language models. It provides tools for chaining together different components to build complex AI applications. LangChain supports various LLMs and provides abstractions for common tasks.',
    'gemini_info.txt': 'Gemini 2.0 Flash is Google\'s latest AI model, optimized for speed and efficiency while maintaining high quality responses. It excels at reasoning, coding, and multimodal understanding. The model supports both text and image inputs.'
}

def call_gemini_api(prompt, api_key):
    """Call Gemini API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")
    
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def find_relevant_docs(question):
    """Simple keyword-based document search"""
    question_lower = question.lower()
    words = [w for w in question_lower.split() if len(w) > 3]
    
    scored = []
    for doc_name, content in documents.items():
        content_lower = content.lower()
        score = sum(1 for word in words if word in content_lower)
        if score > 0:
            scored.append((doc_name, content, score))
    
    scored.sort(key=lambda x: x[2], reverse=True)
    return [(name, content) for name, content, _ in scored[:3]]

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get API key from environment variable
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return jsonify({
                'error': 'API key not configured. Please set GOOGLE_API_KEY environment variable.'
            }), 500
        
        # Find relevant documents
        relevant_docs = find_relevant_docs(question)
        
        # Build prompt with context
        if relevant_docs:
            context = '\n\n'.join([f"[{name}]\n{content}" for name, content in relevant_docs])
            prompt = f"Context from documents:\n\n{context}\n\nQuestion: {question}\n\nBased on the context above, please answer the question."
        else:
            prompt = f"Question: {question}\n\nPlease provide a helpful answer."
        
        # Call Gemini API
        answer = call_gemini_api(prompt, api_key)
        
        return jsonify({
            'answer': answer,
            'sources': [name for name, _ in relevant_docs]
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
        
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are supported'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        # Store in memory
        documents[file.filename] = content
        
        return jsonify({
            'message': f'Document "{file.filename}" uploaded successfully!',
            'total_docs': len(documents)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all loaded documents"""
    return jsonify({
        'documents': list(documents.keys()),
        'count': len(documents)
    })

# For Vercel serverless function
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)