from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable cross-origin requests

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
vector_store_id = os.getenv('VECTOR_STORE_ID')  # Your vector store ID

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        print("Received data:", data)
        
        user_query = data.get('query', '')
        print("User query:", user_query)
        
        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        
        # Get response using RAG
        print("Calling OpenAI API...")
        response = client.responses.create(
            input=[{
                "role": "user", 
                "content": [{"type": "input_text", "text": user_query}]
            }],
            model="gpt-4o-mini",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }]
        )
        print("OpenAI API response received")
        
        # Extract the answer text
        answer = response.output[1].content[0].text
        print("Answer extracted:", answer[:100] + "..." if len(answer) > 100 else answer)
        
        # Get retrieved file information (optional)
        retrieved_files = []
        if hasattr(response.output[1].content[0], 'annotations'):
            for annotation in response.output[1].content[0].annotations:
                retrieved_files.append(annotation.filename)
        
        return jsonify({
            "answer": answer,
            "sources": list(set(retrieved_files)),
            "success": True
        })
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)