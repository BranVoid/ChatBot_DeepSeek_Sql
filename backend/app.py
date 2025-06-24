from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de conocimiento experto
FINANCIAL_KNOWLEDGE = """
Eres un experto en SQL con especialización en finanzas, microfinanzas y análisis comercial. 
Tienes experiencia en modelos de riesgo crediticio, scoring de clientes, análisis de cartera, 
proyecciones financieras y reporting comercial. 

Conocimientos específicos:
- Microfinanzas: Análisis de préstamos grupales, metodología village banking, indicadores de morosidad (PAR), rotación de cartera
- Finanzas: Ratios financieros (liquidez, solvencia, rentabilidad), análisis de estados financieros, proyecciones de flujo de caja
- Comercial: Análisis de canales de venta, segmentación de clientes, CLV (Customer Lifetime Value), análisis de campañas

Siempre que generes consultas:
1. Identifica claramente las suposiciones que estás haciendo sobre la estructura de datos
2. Cuando sea necesario, sugiere estructuras de datos típicas del sector financiero
3. Ofrece explicaciones breves de los conceptos financieros complejos
4. Prioriza consultas que calculen KPIs financieros relevantes
"""

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.route('/generate-query', methods=['POST'])
def generate_query():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Construir el historial de conversación
        messages = [
            {
                "role": "system",
                "content": f"{FINANCIAL_KNOWLEDGE}\n\nInstrucciones adicionales:\n- Genera consultas SQL válidas\n- Explica brevemente tus suposiciones\n- Para términos financieros complejos, ofrece una definición breve\n- Sugiere mejoras en el modelo de datos cuando sea relevante\n- Si la pregunta es ambigua, pide aclaraciones"
            }
        ]
        
        # Agregar historial de conversación si existe
        for msg in conversation_history:
            messages.append(msg)
        
        # Agregar el nuevo mensaje del usuario
        messages.append({
            "role": "user", 
            "content": user_message
        })

        # Generar la respuesta
        chat = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=messages,
            temperature=0.3,  # Menos creatividad, más precisión
            max_tokens=800
        )

        response = chat.choices[0].message.content
        return jsonify({
            "response": response,
            "full_conversation": messages + [{"role": "assistant", "content": response}]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)