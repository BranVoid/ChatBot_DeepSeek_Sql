from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.route('/generate-query', methods=['POST'])
def generate_query():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        chat = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL expert. Generate SQL queries based on the user's requirements. Provide only the SQL query in your response, unless the user asks for an explanation."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
        )

        response = chat.choices[0].message.content
        return jsonify({"query": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)