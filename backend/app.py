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

        # Contexto inicial
        print("Contexto recibido del usuario:", user_message)

        # Generación de múltiples opciones para evaluación
        chat = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL expert. Generate multiple SQL query options based on the user's requirements. Evaluate each option logically and select the best one. Provide only the best SQL query in your response."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
        )

        # Evaluación lógica y selección de la mejor opción
        response = chat.choices[0].message.content
        print("Opciones evaluadas por el modelo:", response)

        # Retorno de la mejor opción
        return jsonify({"query": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)