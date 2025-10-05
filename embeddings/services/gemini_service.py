import requests
from api.config import Config

class GeminiService:
    """Handles Gemini API interactions"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    @staticmethod
    def generate_response(prompt, api_key=None):
        """Generate response from Gemini API"""
        if not api_key:
            api_key = Config.GOOGLE_API_KEY
        
        if not api_key:
            raise ValueError("API key is required")
        
        url = f"{GeminiService.BASE_URL}/{Config.GEMINI_MODEL}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": Config.GEMINI_TEMPERATURE,
                "maxOutputTokens": Config.GEMINI_MAX_TOKENS
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Gemini API Error ({response.status_code}): {error_msg}")
        
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    
    @staticmethod
    def build_prompt_with_context(question, relevant_docs):
        """Build prompt with document context"""
        if relevant_docs:
            context = '\n\n'.join([
                f"[{name}]\n{content}" 
                for name, content, _ in relevant_docs
            ])
            return (
                f"Context from documents:\n\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Based on the context above, please answer the question. "
                f"If the answer is not in the context, you can still provide "
                f"a helpful response but mention that."
            )
        else:
            return f"Question: {question}\n\nPlease provide a helpful answer."