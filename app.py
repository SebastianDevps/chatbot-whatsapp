from flask import Flask, request, render_template   
import services
from flask import jsonify
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)

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
                    is_user BOOLEAN NOT NULL
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
        
        services.administrar_chatbot(text, number, messageId, name)
        return "Enviado"

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/messages')
def view_messages():
    try:
        connection = get_db_connection()
        numberAndMessages = []
        if connection:
            cursor = connection.cursor(cursor_factory=DictCursor)
            
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC")
            
            messages = cursor.fetchall()
            
            # Obtener números de teléfono únicos
            cursor.execute("SELECT DISTINCT phone_number FROM messages")

            phone_numbers = [row['phone_number'] for row in cursor.fetchall()]
            
            for phone in phone_numbers:
                numberAndMessages.append({
                    "phone_number": phone,
                    "messages": [message for message in messages if message['phone_number'] == phone]
                })
            
            cursor.close()
            connection.close()
            
            return numberAndMessages
                                 
    except psycopg2.Error as e:
        print(f"Error en view_messages: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run()

app = app
