from flask import Flask, request, render_template   
import services
from flask import jsonify
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
    
})

def get_db_connection():
    try:
        # Usar la URL completa de conexión
        connection = psycopg2.connect('postgresql://postgres:FjDMYACUWuhiwSPTcsJDVaLFpyyKIeOH@autorack.proxy.rlwy.net:11272/railway')
        print("Conexión exitosa a PostgreSQL")
        return connection
    except psycopg2.Error as e:
        print(f"Error conectando a PostgreSQL: {e}")
        print(f"URL de conexión utilizada: {os.getenv('DATABASE_URL')}")
        return None

def init_db():
    connection = None
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    phone_number VARCHAR(20) NOT NULL,
                    message_text TEXT NOT NULL,
                    response TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    message_id VARCHAR(100),
                    is_user BOOLEAN NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE
                );
                CREATE INDEX IF NOT EXISTS idx_phone_number ON messages(phone_number);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp);
            ''')
            
            connection.commit()
            print("Base de datos inicializada correctamente")
            
    except psycopg2.Error as e:
        print(f"Error inicializando la base de datos: {e}")
    finally:
        if connection:
            connection.close()

# Inicializar la base de datos al arrancar
with app.app_context():
    init_db()

@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola, desde Flask'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == os.getenv('token') and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return str(e), 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        timestamp = int(message['timestamp'])
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        
        services.administrar_chatbot(text, number, messageId, name, timestamp)
        return "Enviado"

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/messages')
def view_messages():
    try:
        number = request.args.get('number')
        connection = get_db_connection()
        
        if connection:
            cursor = connection.cursor(cursor_factory=DictCursor)
            
            if number:
                # Si se proporciona un número, devolver los mensajes ordenados por timestamp
                cursor.execute("""
                    SELECT id, phone_number, message_text, response, 
                           timestamp, message_id, is_user, name 
                    FROM messages 
                    WHERE phone_number = %s 
                    ORDER BY timestamp ASC
                """, (number,))
                
                messages = [dict(message) for message in cursor.fetchall()]
                result = [{
                    "phone_number": number,
                    "messages": messages
                }]
            else:
                # Si no se proporciona número, devolver la lista de números con su último mensaje
                cursor.execute("""
                    SELECT DISTINCT ON (phone_number) 
                        id, phone_number, message_text, response, 
                        timestamp, message_id, is_user, name
                    FROM messages 
                    ORDER BY phone_number, timestamp ASC
                """)
                
                contacts = cursor.fetchall()
                result = [{
                    "phone_number": contact['phone_number'],
                    "messages": []
                } for contact in contacts]
            
            cursor.close()
            connection.close()
            
            return jsonify(result)
                                 
    except psycopg2.Error as e:
        print(f"Error en view_messages: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/messages/read', methods=['POST'])
def mark_as_read():
    try:
        number = request.json.get('number')
        if not number:
            return jsonify({"error": "Number is required"}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE messages 
                SET is_read = TRUE 
                WHERE phone_number = %s
            """, (number,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
