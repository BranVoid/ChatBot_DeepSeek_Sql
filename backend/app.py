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
                    "content": (
                        "You are a SQL expert. Generate multiple SQL query options based on the user's requirements. "
                        "Evaluate each option logically and select the best one. Provide the best SQL query in your response, "
                        "along with a detailed explanation of why it was chosen over the other options."
                    )
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
        )

        # Evaluación lógica y selección de la mejor opción
        query = chat.choices[0].message.content
        print("Evaluación lógica y opciones generadas por el modelo:", response)

        # Retorno de la mejor opción con explicación
        return jsonify({"query": query})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)