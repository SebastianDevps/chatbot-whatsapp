from flask import Flask, request, render_template   
import services
from flask import jsonify
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import certifi

app = Flask(__name__)

# Configuración de MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://guerrasebastian16:<db_password>@chatbot.gixrn.mongodb.net/?retryWrites=true&w=majority&appName=ChatBot')

# Configuración del cliente con opciones simplificadas
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    tlsCAFile=certifi.where(),
    tls=True,
    tlsAllowInvalidCertificates=True,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=30000
)

try:
    db = client['whatsapp_bot']
    messages_collection = db['messages']
except Exception as e:
    print(f"Error inicial al conectar con MongoDB: {e}")
    db = None
    messages_collection = None

def init_db():
    try:
        # Verificar conexión sin usar ping
        dbs = client.list_database_names()
        print("¡Conexión exitosa a MongoDB!")
        print(f"Bases de datos disponibles: {dbs}")
        
        if db and messages_collection:
            # Crear índices si es necesario
            messages_collection.create_index("phone_number")
            messages_collection.create_index("timestamp")
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return False
    return True

# Reemplazar before_first_request con with app.app_context()
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
        phone = request.args.get('phone')
        
        # Consulta de mensajes
        if phone:
            messages = messages_collection.find(
                {"phone_number": phone}
            ).sort("timestamp", -1)
        else:
            messages = messages_collection.find().sort("timestamp", -1)
        
        # Convertir cursor a lista
        messages = list(messages)
        
        # Obtener números de teléfono únicos
        phone_numbers = messages_collection.distinct("phone_number")
        
        return render_template('messages.html', 
                             messages=messages, 
                             phone_numbers=phone_numbers,
                             selected_phone=phone)
    except Exception as e:
        print(f"Error in view_messages: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run()

app = app
