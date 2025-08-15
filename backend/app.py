from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import json
import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuración de directorios
UPLOAD_FOLDER = 'schemas'
TRAINING_DATA_DIR = 'training_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRAINING_DATA_DIR, exist_ok=True)

# Almacenamiento en memoria de esquemas
database_schemas = {}

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

# Obtener API key de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY no está configurada en las variables de entorno")
    raise ValueError("OPENROUTER_API_KEY no está configurada en las variables de entorno")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Servidor operativo"}), 200

@app.route('/upload-schema', methods=['POST'])
def upload_schema():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró el archivo en la solicitud"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
        if file and file.filename.endswith('.txt'):
            filename = secure_filename(file.filename)
            content = file.read().decode('utf-8')
            database_schemas[filename] = content
            
            # Guardar archivo físicamente
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, 'w') as f:
                f.write(content)
                
            return jsonify({
                "message": f"Esquema '{filename}' cargado exitosamente",
                "schemas": list(database_schemas.keys())
            }), 200
        else:
            return jsonify({"error": "Formato de archivo no soportado. Solo se aceptan archivos .txt"}), 400
    except Exception as e:
        logger.exception("Error en upload_schema")
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/get-schemas', methods=['GET'])
def get_schemas():
    return jsonify({
        "schemas": list(database_schemas.keys()),
        "count": len(database_schemas)
    }), 200

def save_training_data(data):
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        filename = f"training_{timestamp}.jsonl"
        file_path = os.path.join(TRAINING_DATA_DIR, filename)
        
        with open(file_path, "a", encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Error al guardar datos de entrenamiento: {str(e)}")

@app.route('/generate-query', methods=['POST'])
def generate_query():
    try:
        # Verificar contenido JSON
        if not request.is_json:
            logger.warning("Solicitud sin contenido JSON")
            return jsonify({"error": "El contenido debe ser JSON"}), 400
            
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        schema_name = data.get('schema', '').strip()

        if not user_message:
            logger.warning("Solicitud sin mensaje")
            return jsonify({"error": "El mensaje es requerido"}), 400

        # Construir el historial de conversación
        messages = [
            {
                "role": "system",
                "content": f"{FINANCIAL_KNOWLEDGE}\n\nInstrucciones adicionales:\n- Genera consultas SQL válidas\n- Explica brevemente tus suposiciones\n- Para términos financieros complejos, ofrece una definición breve\n- Sugiere mejoras en el modelo de datos cuando sea relevante\n- Si la pregunta es ambigua, pide aclaraciones"
            }
        ]
        
        # Agregar esquema si está disponible
        if schema_name and schema_name in database_schemas:
            messages[0]["content"] += f"\n\nEsquema de base de datos actual:\n{database_schemas[schema_name]}"
        
        # Validar y agregar historial de conversación
        if isinstance(conversation_history, list):
            for msg in conversation_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Agregar el nuevo mensaje del usuario
        messages.append({
            "role": "user", 
            "content": user_message
        })

        # Llamar a la API de OpenRouter
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "SQL Financial Assistant"
        }
        
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        logger.info(f"Enviando solicitud a OpenRouter con {len(messages)} mensajes")
        
        # Hacer la solicitud con timeout
        response = requests.post(openrouter_url, headers=headers, json=payload, timeout=30)
        
        # Verificar si la respuesta está vacía
        if not response.text:
            logger.error("Respuesta vacía de OpenRouter")
            return jsonify({
                "error": "La API devolvió una respuesta vacía"
            }), 500
            
        # Intentar parsear la respuesta
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error(f"No se pudo parsear la respuesta como JSON. Status: {response.status_code}, Contenido: {response.text[:500]}")
            return jsonify({
                "error": f"Respuesta inválida de la API. Código: {response.status_code}"
            }), 500
        
        # Verificar errores en la respuesta
        if 'error' in response_data:
            error_msg = response_data['error'].get('message', 'Error desconocido')
            logger.error(f"Error de OpenRouter: {error_msg}")
            return jsonify({
                "error": f"Error en OpenRouter: {error_msg}"
            }), 500
        
        if 'choices' not in response_data or not response_data['choices']:
            logger.error(f"Respuesta inesperada de OpenRouter: {response_data}")
            return jsonify({
                "error": "Respuesta inesperada de la API: no contiene 'choices'"
            }), 500
        
        chat_response = response_data['choices'][0]['message']['content']
        
        # Guardar para entrenamiento
        training_record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "schema_used": schema_name,
            "assistant_response": chat_response,
            "full_conversation": messages + [{"role": "assistant", "content": chat_response}]
        }
        save_training_data(training_record)

        return jsonify({
            "success": True,
            "response": chat_response,
            "full_conversation": training_record["full_conversation"],
            "timestamp": training_record["timestamp"]
        }), 200

    except requests.exceptions.Timeout:
        logger.error("Timeout al conectar con OpenRouter")
        return jsonify({
            "success": False,
            "error": "Timeout al conectar con el servicio de generación"
        }), 504
        
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión con OpenRouter")
        return jsonify({
            "success": False,
            "error": "Error de conexión con el servicio de generación"
        }), 503
        
    except requests.exceptions.HTTPError as http_err:
        logger.exception("Error HTTP en OpenRouter")
        return jsonify({
            "success": False,
            "error": f"Error HTTP: {str(http_err)}"
        }), 500
        
    except json.JSONDecodeError as json_err:
        logger.exception("Error decodificando JSON de OpenRouter")
        return jsonify({
            "success": False,
            "error": "Error procesando la respuesta del servicio de generación"
        }), 500
        
    except Exception as e:
        logger.exception("Error inesperado en generate_query")
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/get-training-data', methods=['GET'])
def get_training_data():
    try:
        date = request.args.get('date', datetime.utcnow().strftime("%Y%m%d"))
        filename = f"training_{date}.jsonl"
        file_path = os.path.join(TRAINING_DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "No hay datos para la fecha especificada"}), 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f.readlines()]
            
        return jsonify({
            "count": len(data),
            "date": date,
            "data": data
        }), 200
    except Exception as e:
        logger.exception("Error en get_training_data")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')