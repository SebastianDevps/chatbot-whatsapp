from flask import Flask, request, render_template   
import services
from flask import jsonify
import os
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile

app = Flask(__name__)

# Usar directorio temporal para la base de datos
DB_PATH = os.path.join(tempfile.gettempdir(), 'messages.db')

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                message_text TEXT,
                response TEXT,
                timestamp DATETIME,
                message_id TEXT,
                is_user BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()

# Llamar a init_db al inicio de la aplicación
init_db()

@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
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
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        print(body)
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
        
        response = services.administrar_chatbot(text, number,messageId,name)
        print("response webhook: ", response)
        return "Enviado"

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/messages')
def view_messages():
    try:
        conn = sqlite3.connect(os.environ.get('DB_PATH'))
        c = conn.cursor()
        
        phone = request.args.get('phone')
        
        if phone:
            c.execute('SELECT * FROM messages WHERE phone_number = ? ORDER BY timestamp DESC', (phone,))
        else:
            c.execute('SELECT * FROM messages ORDER BY timestamp DESC')
        
        messages = c.fetchall()
        
        c.execute('SELECT DISTINCT phone_number FROM messages')
        phone_numbers = [row[0] for row in c.fetchall()]
        
        return render_template('messages.html', 
                             messages=messages, 
                             phone_numbers=phone_numbers,
                             selected_phone=phone)
    except Exception as e:
        print(f"Error in view_messages: {e}")
        return str(e), 500
    finally:
        conn.close()


    
    # Inicializar la base de datos al arrancar
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run()
    # app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))


app = app
