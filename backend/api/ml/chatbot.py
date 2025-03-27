from flask import Blueprint, request, jsonify
import requests
import os

chat_bp = Blueprint('chat', __name__)

# Get API key from environment variable
API_KEY = os.getenv("PERPLEXITY_API_KEY", "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")

def ask_perplexity(prompt: str) -> str:
    """Helper function to query Perplexity API"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Error: {str(e)}"

@chat_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    """Endpoint for handling chat requests"""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400
    
    user_message = data['message']
    try:
        ai_response = ask_perplexity(user_message)
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500